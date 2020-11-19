#!/usr/bin/env python
from __future__ import print_function
import os.path
import os
import sys
import glob
import zipfile
import traceback
from lxml import etree, builder
import datetime
import shutil

UMI_to_DSPACE = "proquest_configs/UMI_to_DSpaceDC.xsl"
COLLECTION_MAP = "proquest_configs/collection_map.xml"

PROQUEST_EMBARGO_CODE = 4
PROQUEST_ROOT_TAG = 'DISS_submission'
PROQUEST_ROOT_TAG = 'DISS_submission'
PROQUEST_EMBARGO_ATTR = 'embargo_code'
PROQUEST_EMBARGO_END = '*/DISS_sales_restriction'

REJECT_DIR = 'REJECTS'
SUCCESS_DIR = 'SUCCESS'


def do_dissertations(dir_name, unzip_dir):
    """
    prepare disserations in <dir_name/*.zip files, aka unzip and create AIP related pacakge files in unzip_dir

    :param dir_name:
    :param unzip_dir:
    :return:  0 if succesfull on all dissertation zip archives otherwise return number of failed diserations
    """
    nsuccess, nreject = 0, 0
    reject_dir = _get_dir(unzip_dir, REJECT_DIR)
    if _create_dirs(unzip_dir):
        zips = glob.glob("{}/*.zip".format(dir_name))
        i = 0
        for z in zips:
            i = i + 1
            print("#{} {} ".format(i, z))
            data_xml, dcore, puxml, dcontents, dcollection = None, None, None, None, None
            dname = unzip_dissertation(i, z, _get_dir(unzip_dir, SUCCESS_DIR))
            if (dname):
                try:
                    data_xml = _get_DATA_xml_file(i, dname)
                    dcore = generate_dublincore(i, dname, data_xml)
                    puxml = generate_metadata_pu(i, dname, data_xml)
                    dcontents = generate_contents(i, dname)
                    dcollection = generate_collections(i, dname, dcore)
                except Exception as e:
                    eprint("#{} ERROR: ".format(i, str(e)))
                    traceback.print_exc()
            if dname and data_xml and dcore and puxml and dcontents and dcollection:
                nsuccess += 1
                print("#{} SUCCESS {}".format(i, os.path.basename(dname)))
            else:
                nreject += 1
                eprint("#{} ERROR: something went wrong with {} - moving to {}".format(i, dname if dname else z,
                                                                                       reject_dir))
                if dname:
                    to = "{}/{}".format(reject_dir, os.path.basename(dname))
                    if os.path.isdir(to):
                        shutil.rmtree(to)
                    os.rename(dname, to)
                else:
                    os.rename(z, '{}/{}'.format(reject_dir, os.path.basename(z)))

            print('')

        print("SUCCESS on {} dissertations".format(nsuccess))
        print("REJECT for {} dissertations".format(nreject))
        print('')
        if i == 0:
            print("WARN: no matches for {}/*.zip".format(dir_name))
        if nreject + nsuccess != i:
            print("ERROR: this SHOULD NEVER HAPPEN nuccess{} + nreject{} != total{}".format(nsuccess, nreject, i))
            return 1
        if (nreject == 0):
            os.rmdir(reject_dir)
            print("delete " + reject_dir)
        return nreject


def unzip_dissertation(i, z, unzip_dir):
    dname = os.path.basename(z).split('.')[0]
    dname = '{}/{}'.format(unzip_dir, dname)
    print("#{} unzip {} to {}".format(i, z, dname))
    try:
        os.mkdir(dname)
        zip_ref = zipfile.ZipFile(z, 'r')
        zip_ref.extractall(dname)
        return dname
    except Exception as e:
        eprint("#{} ERROR could not unzip {} to {}: {}".format(i, z, dname, str(e)))
        return None


def generate_dublincore(i, dname, data_xml):
    if not data_xml: return None
    gen_file = _make_file(i, dname, 'dublin_core.xml')
    cmd = 'xsltproc --output {}  {} {}'.format(gen_file, UMI_to_DSPACE, data_xml)
    rc = os.system(cmd)
    if (rc != 0):
        eprint("#{} ERROR {}".format(i, cmd))
        return None
    return gen_file


def generate_metadata_pu(i, dname, data_xml):
    if not data_xml: return None
    try:
        end_date = _embargo_end(data_xml)
        if (end_date):
            gen_file = _make_file(i, dname, 'metadata_pu.xml', ' embargo_end_date: {}'.format(end_date))
            _build_metadata_pu(gen_file, end_date)
    except Exception as e:
        eprint("#{} ERROR: Could not determine embargo status {}: {}".format(i, data_xml, str(e)))
    return True  # succesfully generated OR NOOP


def generate_contents(i, dname):
    docs = []
    for doc in os.listdir(dname):
        if doc not in ['contents', 'dublin_core.xml', 'collections', 'metadata_pu.xml'] and not doc.endswith(
                'DATA.xml'):
            doc_path = '{}/{}'.format(dname, doc)
            if os.path.isdir(doc_path):
                for incl in os.listdir(doc_path):
                    docs.append('{}/{}'.format(doc, incl))
            else:
                docs.append(doc)
    if not docs:
        eprint("#{} ERROR {}".format(i, "No contents files"))
        return False
    else:
        fp = open(_make_file(i, dname, 'contents', "#files {}".format(len(docs))), 'w')
        print("\n".join(docs), file=fp)
        fp.close()
        return True


def generate_collections(i, dname, dcore):
    gen_file = _make_file(i, dname, 'collections')
    handles = []
    error = False
    for col in _dublincore_other_contributors(dcore):
        handle = _collection_handle(col)
        if (handle):
            handles.append(handle)
        else:
            eprint(u"#{} ERROR: no matching collection for '{}'".format(i, col))
            error = True
    if (handles):
        fp = open(gen_file, 'w')
        print("\n".join(handles), file=fp)
        fp.close()
    else:
        error = True
    return not error


def _build_metadata_pu(fname, end_date):
    maker = builder.ElementMaker()
    the_doc = maker.dublin_core(
        maker.dcvalue(end_date, element="embargo", qualifier="terms"),
        maker.dcvalue(end_date, element="embargo", qualifier="lift"),
        schema="pu"
    )
    ed = open(fname, 'w')
    print(etree.tostring(the_doc, pretty_print=True), file=ed)
    ed.close()


def _dublincore_other_contributors(dcore):
    if (dcore):
        with open(dcore, 'r') as fp:
            tree = etree.parse(fp)
            for el in tree.findall('.//dcvalue[@qualifier="other"]'):
                col = el.text
                if col.endswith('Department'):
                    col = col[:-len('Department')]
                    yield col.strip()
                else:
                    yield col


def _embargo_end(data_xml):
    fp = None
    try:
        fp = open(data_xml, 'r')
        root = etree.parse(fp).getroot()
        if not root.tag == PROQUEST_ROOT_TAG:
            raise Exception("{} is not root element".format(PROQUEST_ROOT_TAG))
        if PROQUEST_EMBARGO_CODE == _get_embargo_code(root):
            return _get_embargo_end(root)
    finally:
        if (fp):
            fp.close()
    return None


def _get_embargo_code(root):
    code = -1
    if PROQUEST_EMBARGO_ATTR in root.attrib:
        code = int(root.attrib[PROQUEST_EMBARGO_ATTR])
    return code


def _get_embargo_end(root):
    end_date = root.find(PROQUEST_EMBARGO_END).attrib['remove']
    date_time_obj = datetime.datetime.strptime(end_date, '%m/%d/%Y')
    return date_time_obj.date().isoformat()


_collection_map = {}


def _build_collection_map():
    if not _collection_map:
        with open(COLLECTION_MAP, 'r') as fp:
            tree = etree.parse(fp)
            for el in tree.findall('.//collection'):
                name = el.find('name').text
                handle = el.find('identifier').text
                _collection_map[name] = handle
    return _collection_map


def _collection_handle(col):
    col_map = _build_collection_map()
    if col in col_map:
        return col_map[col]
    else:
        return None


def _make_file(i, dname, fname, extra=""):
    gen_file = '{}/{}'.format(dname, fname)
    print("#{} make {} {}".format(i, gen_file, extra))
    return gen_file


def _get_dir(dname, sub_dir):
    return '{}/{}'.format(dname, sub_dir)


def _create_dirs(name):
    try:
        if not os.path.isdir(name):
            os.mkdir(name)
            print("create: " + name)
        for d in [SUCCESS_DIR, REJECT_DIR]:
            d_dir = _get_dir(name, d)
            if not os.path.isdir(d_dir):
                os.mkdir(d_dir)
                print("create: " + d_dir)
    except Exception as e:
        eprint(e)
        eprint("ERROR: could not create {}".format(name))
        return None
    return True


def _get_DATA_xml_file(i, dname):
    data_xml = glob.glob("{}/*_DATA.xml".format(dname))
    if (len(data_xml) != 1):
        eprint("#{} ERROR: Can't identify unique *_DATA.xml in {}".format(i, dname))
        return None
    return data_xml[0]


def eprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs)


if __name__ == '__main__':
    dir_name = sys.argv[1]
    to_dir = sys.argv[2]
    rc = do_dissertations(dir_name, to_dir)
    sys.exit(rc)
