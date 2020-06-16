import os
import sys
import shutil
import logging


_nerror = 0

def _error(msg):
    global _nerror
    _nerror = _nerror + 1
    logging.error(msg)
    return None

def _info(pre, msg):
    logging.info('{}: {}'.format(pre, msg))
    return None

def _debug(pre, msg):
    logging.debug('{}: {}'.format(pre, msg))
    return None

SKIP = 'SKIP'
IMPORT = 'IMPORT'
DONE = 'DONE'
INTERNAL = 'INTERNAL'

def _mapfile(tgz):
    return '{}/imports/{}.mapfile'.format(s3_mirror, tgz)

def _logfile(tgz):
    return '{}/imports/{}.log'.format(s3_mirror, tgz)

def _check_status(tgz, s3_files):
    if tgz.endswith('.mapfile') or tgz == 'log' or tgz == 'imports':
        return INTERNAL
    if not tgz.endswith('tgz'):
        return SKIP
    if os.path.exists(_mapfile(tgz)):
        return DONE
    else:
        return IMPORT

def _systm(s3_file, cmd, logfile):
    logging.info(cmd)
    with open(logfile,"a+") as f: f.write('> ' + cmd + '\n')
    rc = os.system('({}) >> {}  2>&1'.format(cmd, logfile))
    if 0 != rc:
        msg = '{} rc={}'.format(cmd, rc)
        _error(msg)
        with open(logfile,"a+") as f: f.write('ERROR\n')
    return rc

def _unpack(s3_dir, s3_file, logfile):
    try:
        dirname = s3_file.split('.')[0]
        os.mkdir(dirname)
        os.mkdir('{}/{}'.format(dirname, dirname))
    except:
        return _error('could not create {}/{}'.format(dirname, dirname))

    cmd = 'cd {}/{}; tar xvfz  {}/{}'.format(dirname, dirname, s3_dir, s3_file)
    rc = _systm(s3_file, cmd, logfile)
    if 0 == rc:
        return dirname
    else:
        return None


def _dataspace_import_cmd(aip_dir, submitter, mapfile):
    import_cmd = '{}/bin/dspace import --add --workflow -notify  -e {} --mapfile {} -s {} '
    import_cmd = import_cmd.format(dspace_home, submitter, mapfile, aip_dir)
    return import_cmd


def _check_mapfile(s3_file):
    mapfile = _mapfile(s3_file)
    #check exists and is not empty
    ok =   (os.path.isfile(mapfile) and 0 < os.path.getsize(mapfile))
    if not ok:
        _error('broken mapfile for {}'.format(s3_file))
    return ok


def _cleanup_dir(dirname):
    if dirname:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            logging.info('rmtree ' + dirname)
        else:
            logging.error('directory "{}" does not exist'.format(dirname))


def _cleanup_file(fname):
    if os.path.exists(fname):
        os.remove(fname)
        logging.info('rmfile ' + fname)


def _import(s3_mirror, log, submitter, s3_file):
    success = False
    dir = None
    mapfile = _mapfile(s3_file)
    try:
        logfile = _logfile(s3_file)
        logging.info('logging {} import to {}'.format(s3_file, logfile))
        dir = _unpack(s3_mirror, s3_file, logfile)
        if dir:
            cmd = _dataspace_import_cmd(dir, submitter, mapfile)
            rc = _systm(s3_file, cmd, logfile)
            success = rc == 0 and _check_mapfile(s3_file)
    except:
        pass;
    _cleanup_dir(dir)
    logging.info('{} {}'.format(s3_file, 'SUCCESS' if success else 'FAILURE'))
    if not success:
        _cleanup_file(mapfile)
        #_cleanup_file('{}/{}'.format(s3_mirror, s3_file))

    logging.info('----')



def _work_aips(s3_mirror, log, submitter):
    logging.info('SETUP local-bucket-mirror:  {}'.format(s3_mirror))
    logging.info('SETUP log-directory:  {}'.format(log))
    logging.info('SETUP submitter:  {}'.format(submitter))

    s3_files = os.listdir(s3_mirror)
    for e in s3_files:
        status = _check_status(e, s3_files)
        if (status != INTERNAL):
            _debug(e, str(status))
            if (status == IMPORT):
                _import(s3_mirror, log, submitter, e)
    return _nerror


dspace_home =  os.getenv('DSPACE_HOME')
submitter =  os.getenv('SUBMITTER')
s3_mirror =  os.path.abspath(os.getenv('S3'))
oglevel =  os.getenv('LOG_LEVEL')
log = '{}/log'.format(s3_mirror)

logging.getLogger().setLevel(loglevel)
if 0 == _work_aips(s3_mirror, log, submitter):
    logging.info('SUCCESS all packages imported')
    sys.exit(0)
else:
    _error('failed to import {} packages'.format(_nerror))
    sys.exit(1)
