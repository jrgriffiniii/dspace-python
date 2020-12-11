import os
import sys
import shutil
import logging
import argparse
import pathlib2 as pathlib
from pathlib2 import Path

import pdb

if len(sys.argv) < 4:
    raise Exception('Usage: dataspace_import.py $DSPACE_HOME $DSPACE_EPERSON $S3_PATH')

DSPACE_HOME = sys.argv[1]
SUBMITTER = sys.argv[2]
S3_MIRROR = sys.argv[3]

LOGLEVEL = "DEBUG"
SKIP = 'SKIP'
IMPORT = 'IMPORT'
DONE = 'DONE'
INTERNAL = 'INTERNAL'

s3_file_batch_size = 0
_nerror = 0

def _error(msg):
    """
    Log a message for the error log

    """

    global _nerror
    _nerror = _nerror + 1
    logging.error(msg)

    return None

def _info(pre, msg):
    """
    Log a message for the info log

    """

    logging.info('{}: {}'.format(pre, msg))

    return None

def _debug(pre, msg):
    """
    Log a message for the debugging log

    """
    logging.debug('{}: {}'.format(pre, msg))

    return None

def _systm(s3_file, cmd, logfile):
    """
    execute a command using the bash

    parameters
    ----------
    s3_file : str
        the path to the file
    cmd : str
        the command being executed in the shell
    logfile : str
        the path to the logging file

    returns
    -------
    int
        the return code of the command

    """
    with open(logfile,"a+") as f: f.write('> ' + cmd + '\n')
    rc = os.system('({}) >> {} 2>&1'.format(cmd, logfile))

    if 0 != rc:
        msg = '{} rc={}'.format(cmd, rc)
        _error(msg)
        with open(logfile,"a+") as f: f.write('error\n')
    return rc

def _unpack(s3_dir, s3_file, logfile):
    """
    Decompress the GZipped TAR into a directory

    Parameters
    ----------
    s3_dir : str
        The directory path for the S3 synchronization
    s3_file : str
        The TAR file from the S3 Bucket
    logfile : str
        The path to to the log file

    Returns
    -------
    str
        The name of the directory where the TAR has been decompressed
    """
    try:
        segments = s3_file.split('.')
        dirname = "{}/imports/{}".format(S3_MIRROR, segments[0])
        # This structure is required for DSpace imports
        item_dirname = "{}/{}".format(dirname, "item_000")

        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            os.makedirs(item_dirname)
    except Exception as error:
        logging.error(str(error))
        return _error('could not create {}'.format(dirname))

    cmd = 'cd {}; tar xvfz {}/{}; cd -'.format(item_dirname, s3_dir, s3_file)
    rc = _systm(s3_file, cmd, logfile)
    if 0 == rc:
        return Path(dirname)
    else:
        return None

def _ingest(s3_mirror, log, submitter, s3_file, import_service):
    """
    Import a file into DSpace given the file path

    Parameters
    ----------
    s3_mirror : str
        The directory path for the S3 synchronization
    log : Object
        The system logger
    submitter: str
        Submitter account
    s3_file : str
        File path for the file in the S3 Bucket
    import_service : Object
        Importer service
    """

    success = False
    unpacked_dir = None
    s3_file_path = Path(s3_file)

    mapfile_path = import_service.build_mapfile_path(s3_file_path)
    if mapfile_path.exists():
        import_service.logger.info('Removing the empty mapfile {}'.format(mapfile_path))
        mapfile_path.unlink()

    logfile = import_service._logfile(s3_file)
    try:
        decompressed_dir_path = _unpack(import_service.s3_mirror, s3_file, logfile)

        if decompressed_dir_path.exists():
            cmd = import_service._dataspace_import_cmd(decompressed_dir_path, mapfile_path)

            rc = _systm(s3_file, cmd, logfile)
            success = rc == 0 and import_service.isarchived(s3_file_path)
    except:
        pass

    success_state = 'SUCCESS' if success else 'FAILURE'
    import_service.logger.info('Import status for {}: {}'.format(s3_file, success_state))
    if not success:
        logging.info('Please check the logging entries in {}'.format(logfile))

    logging.info('----')

class Package:
    def __init__(self, path):
        self.path = path

class PackageDirectory:

    def __init__(self, path, import_service):
        self._path = path
        self._import_service = import_service

        self._files = os.listdir(self._path)
        self._packages = self.parse_files()

    def isnewpackage(package_path):
        return ImportService.ispackagepath(package_path) and not self._import_service.isarchived(package_path)

    def parse_files(self):
        packages = []

        for s3_file in self._files:
            s3_file_path = pathlib.Path(s3_file)

        if self.isnewpackage(s3_file_path):
            package = Package(s3_file_path)
            packages.append(package)

        self._packages = packages
        return self._packages

    def ingest(self):
        for package in self._packages:
            self._import_service.ingest(package)
            # self._import_service.logger.info("Importing {}".format(package.path))
            # _import(self._import_service.s3_mirror, self._import_service.log, import_service.eperson, package, import_service)

    pass

class ImportService:
    # This needs to be refactored
    @classmethod
    def aws_s3_path(cls):
        return S3_MIRROR

    @classmethod
    def ispackagepath(cls, file_path):
        return file_path.suffix == '.tgz'

    def build_mapfile_path(self, archive_path):
        mapfile_name = "{}.mapfile".format(archive_path.name)
        path = Path(self.aws_s3_path, 'imports', mapfile_name)

        return path

    def isarchived(self, file_path):
        mapfile_path = self.build_mapfile_path(file_path)
        status = mapfile_path.exists() and mapfile_path.stat().st_size > 0

        return status

    def _dataspace_import_cmd(self, sip_dir, mapfile):
        """
        Import a directory into DataSpace

        Parameters
        ----------
        sip_dir : str
            The directory path for the submission information package
        submitter : str
            The e-mail address of the submitter account in DSpace
        mapfile : str
            The file path to the DSpace import mapfile
        """

        import_cmd = '{}/bin/dspace import --add --workflow --eperson {} --mapfile {} --source {}'
        cmd = import_cmd.format(self.dspace_home, self.eperson, mapfile, sip_dir)
        self.logger.info(cmd)

        return cmd

    def _log_error(self, message):
        global _nerror
        _nerror = _nerror + 1
        logging.error(message)

    def _execute(self, command, logfile):

        with open(logfile, "a+") as f:
            f.write('> ' + command + '\n')

        return_code = os.system('({}) >> {} 2>&1'.format(command, logfile))

        if 0 != return_code:
            message = '{} rc={}'.format(command, return_code)

            # _error(msg)
            self._log_error(message)

            with open(logfile, "a+") as f:
                f.write('error\n')

        return return_code

    def import_into_dspace(self, source_path, mapfile_path):

        cmd = self._dataspace_import_cmd(source_path, mapfile_path)
        # rc = _systm(s3_file, cmd, logfile)
        return_code = self._execute(command, logfile)
        success = return_code == 0 and self.isarchived(s3_file_path)

        return success

    def _unpack(self, package, logfile):
        try:
            segments = package.path.split('.')
            dirname = "{}/imports/{}".format(S3_MIRROR, segments[0])
            # This structure is required for DSpace imports
            item_dirname = "{}/{}".format(dirname, "item_000")

            if not os.path.isdir(dirname):
                os.makedirs(dirname)
                os.makedirs(item_dirname)
        except Exception as error:
            logging.error(str(error))
            return self._log_error('could not create {}'.format(dirname))

        cmd = 'cd {}; tar xvfz {}/{}; cd -'.format(item_dirname, s3_dir, s3_file)
        rc = self._execute(cmd, logfile)
        if 0 == rc:
            return Path(dirname)

    def ingest(self, package):
        success = False
        unpacked_dir = None

        s3_file_path = Path(package.path)

        # Replace this with package.mapfile
        mapfile_path = self.build_mapfile_path(s3_file_path)
        if mapfile_path.exists():
            self.logger.info('Removing the empty mapfile {}'.format(mapfile_path))
            mapfile_path.unlink()

        # Replace this with package.logfile
        logfile = self._logfile(package.path)
        try:
            # decompressed_dir_path = _unpack(self.s3_mirror, s3_file, logfile)
            decompressed_dir_path = self._unpack(package, logfile)

            if decompressed_dir_path.exists():
                # cmd = self._dataspace_import_cmd(decompressed_dir_path, mapfile_path)

                # rc = _systm(s3_file, cmd, logfile)
                # success = rc == 0 and self.isarchived(s3_file_path)
                success = self.import_into_dspace(decompressed_dir_path, mapfile_path)
        except:
            # This needs to be handled
            pass

        success_state = 'SUCCESS' if success else 'FAILURE'
        self.logger.info('Import status for {}: {}'.format(package, success_state))
        if not success:
            logging.info('Please check the logging entries in {}'.format(logfile))

    def _logfile(self, tgz):
        """
        Generate the file path for the DSpace import log file given a file name

        Parameters
        ----------
        tgz : str
            The path to the file
        """

        return '{}/imports/{}.log'.format(self.s3_mirror, tgz)

    def configure_logging(self):
        logger_level = logging.DEBUG

        logger = logging.getLogger()
        logger.setLevel(logger_level)

        self.logger = logger
        return self.logger

    def parse_args(self):
        parser = argparse.ArgumentParser(description='Import PPPL submission information packages into DataSpace.')

        parser.add_argument("-d", "--dspace-home", help="DSpace home directory")
        parser.add_argument("-e", "--eperson", help="DSpace EPerson e-mail account")
        parser.add_argument("-s", "--s3-mirror", help="Amazon Web Services S3 mirror directory")
        parser.add_argument("-v", "--verbose", help="Increase the verbosity of the logging", action="count")
        args = parser.parse_args()

        self.args = args
        return self.args

    def __init__(self, dspace_home, s3_mirror, eperson):
        self.dspace_home = dspace_home
        # This attribute should be renamed
        self.s3_mirror = s3_mirror
        self.aws_s3_path = self.s3_mirror
        self.eperson = eperson
        self.log = '{}/log'.format(self.s3_mirror)

if __name__=="__main__":

    import_service = ImportService(DSPACE_HOME, S3_MIRROR, SUBMITTER)
    import_service.configure_logging()

    s3_file_batch_size = 0
    _nerror = 0

    # exit_code = _work_sips(import_service)

    logging.info('SETUP local-bucket-mirror:  {}'.format(import_service.s3_mirror))
    logging.info('SETUP log-directory:  {}'.format(import_service.log))
    logging.info('SETUP submitter:  {}'.format(import_service.eperson))

    package_dir = PackageDirectory(S3_MIRROR, import_service)
    exit_code = package_dir.ingest()

    if exit_code == 0:
        import_service.logger.info('SUCCESS all packages imported')
        sys.exit(0)
    else:
        _error('failed to import {} packages'.format(s3_file_batch_size))
        sys.exit(exit_code)
