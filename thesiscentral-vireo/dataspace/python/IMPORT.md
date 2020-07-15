# Importing DataSpace Items

## Importing Thesis Central (Vireo) submissions into DataSpace (DSpace)
Thesis Central submissions are organized by academic departments.

## Preparing a local environment

### Installing `pipenv`

```
# For Python 3.x support:
pyenv local 3.8.3

# Or, for legacy support:
pyenv local 2.7.18

pip install pipenv
```

### Installing the Python package dependencies

#### 3.8.3

```
pipenv --python 2.7.18 shell
pipenv lock --pre
pipenv install
```

#### 2.7.18

```
cp Pipfile.legacy Pipfile
cp Pipfile.legacy.lock Pipfile
pipenv --python 2.7.18 shell
pipenv lock --pre
pipenv install
```

### Tunneling over SSH

In order to execute these scripts, one must first tunnel over SSH for copying
files using `scp`:

```bash
ssh -L 1234:dataspace.princeton.edu:22 $USER@epoxy.princeton.edu
```

...where `$USER` is an OIT service account used to access the production or QA
server environments for DSpace.

## Exporting from Thesis Central
Users must export Excel Spreadsheet after selecting a department from [Thesis Central](thesis-central.princeton.edu).

Please note that one must include the following columns in the export:

* ID
* Thesis Type
* Certificate Program
* Department
* Student name
* Student email
* Multi Author
* Institutional ID
* Submission date
* Advisors
* Document language
* Document title
* Status
* Primary document
* Approval date
* Event time

Please note that the `status` value of `Submitted` will not be assumed to be
`Approved`, hence, these will simply not be handled by the import scripts.

![alt text](./docs/thesis-central_screenshot_4.png)

One then exports both the `Excel Export (with Document URLs)`:

![alt text](./docs/thesis-central_screenshot_5.png)

...as well as the `DSpace Simple Archive`:

![alt text](./docs/thesis-central_screenshot_6.png)

Please download the Excel Export into `downloads/ExcelExport.xlsx`, and the 
DSpace Simple Archive into `downloads/DSpaceSimpleArchive.zip`.

## Applying Restrictions

One must then export the submission restrictions from the University Sharepoint
provided by the Office of the Registrar (please download the latest export from 
[Google Drive](https://drive.google.com/file/d/1yVsV5PG-WPtj-eV7lHGRbuj3sVUGdwZh/view?usp=sharing) to `downloads/Restrictions.xlsx`).

Then, one must copy the file, and add an `ID` column to this exported Spreadsheet:
```
cp downloads/Restrictions.xlsx downloads/RestrictionsWithId.xlsx
```

![alt text](./docs/thesis-central_screenshot_1.png)
![alt text](./docs/thesis-central_screenshot_2.png)

Finally, one must update the spreadsheet with the following:

```bash
/bin/tcsh
set department="Mechanical & Aerospace Engr"

# This shouldn't be necessary, but requires that the Python scripts be rewritten
cp downloads/RestrictionsWithId.xlsx export/RestrictionsWithId.xlsx
cp downloads/RestrictionsWithId.xlsx export/$department/RestrictionsWithId.xlsx

/usr/bin/env pipenv run python restrictionsFindIds.py --thesis export/$department/ExcelExport.xlsx --restrictions export/$department/RestrictionsWithId.xlsx
cp ImportRestrictions.xlsx export/$department/RestrictionsWithId.xlsx
```

## Adding the Academic Programs

Academic programs are listed in a spreadsheet located on [Google
Drive](https://drive.google.com/file/d/1K_rrBPY-Pf3DcqbCS-ZxYFjMQl3bIYEM/view?usp=sharing).

This should please be downloaded and copied with the following:
```
cp ~/AdditionalPrograms.xlsx export/AdditionalPrograms.xlsx
cp ~/AdditionalPrograms.xlsx export/$department/AdditionalPrograms.xlsx
```

## Building DSpace Submission Information Packages (SIPs)

Please note that this assumes that you have downloaded the Thesis Central 
departmental Excel Spreadsheet into `downloads/ExcelExport.xlsx`, and
the departmental DSpace Simple Archive into `downloads/DSpaceSimpleArchive.zip`.

### Cleaning the Environment

```bash
/bin/tcsh
set department="English"
source clean-simple-archives
```

### Initializing the Environment

```bash
/bin/tcsh
set department="English"
source init-simple-archives
```

### Building SIPs

```bash
/bin/tcsh
set department="English"
pipenv install lxml pandas

# Please note that the DSpaceSimpleArchive is decompressed
rm ./DSpaceSimpleArchive
unzip DSpaceSimpleArchive.zip

source prepare-to-dataspace "export/$department"

# Or, for when debugging
source prepare-to-dataspace "export/$department" --debug
```

## Multi-Author Submissions

```bash
/bin/tcsh
set department="Mechanical & Aerospace Engr"
source clean-simple-archives
source init-simple-archives
```

```bash
/bin/tcsh
set department="Mechanical & Aerospace Engr"
pipenv install lxml pandas

# Please note that the DSpaceSimpleArchive is decompressed
rm ./DSpaceSimpleArchive
unzip DSpaceSimpleArchive.zip

source prepare-to-dataspace "export/$department"
```

### Transfer the SIPs to the server

```bash
/bin/tcsh
set user=SSH_USER
set host=updatespace.princeton.edu # Or, for production, dataspace.princeton.edu
set department="Mechanical & Aerospace Engr"

scp -P 1234 "export/$department/$department.tgz" $user@localhost:"/var/scratch/thesis-central/"
ssh -J $user@epoxy.princeton.edu $user@$host chmod o+r "/var/scratch/thesis-central/$department.tgz"
```

## Import to DataSpace

From the DataSpace server environment, please invoke the following:

```bash
/bin/tcsh
set department="Mechanical & Aerospace Engr"
ssh -J $user@epoxy.princeton.edu $user@$host
su - root
su - dspace
cd ~/thesiscentral-vireo/dataspace/import
```

One must ensure that the directory used for imports is clean of previous import
procedures:

```bash
unlink /dspace/www/thesis_central/$department/$department.tsv
unlink /dspace/www/thesis_central/$department/Approved
rm -rf /dspace/www/thesis_central/$department/tc_export/
```

### Building Multi-Author Directories

```bash
mkdir /dspace/www/thesis_central/Multi-Author
mkdir -p /dspace/www/thesis_central/Multi-Author/Approved/$department
```

Then please invoke:

```bash
/bin/tcsh
set department=English

source ./unwrap

# This is necessary until the unwrap procedure is reimplemented

mkdir tc_export
mv "$department.tsv" tc_export/
mv Approved tc_export/

# This is necessary due to certain export limitations for metadata_pu.xml files
grep -lr 'is not supported by the DSpace Simple Archive format' "/dspace/www/thesis_central/$department/tc_export/Approved/" | xargs rm

# Then import to DSpace using the following:

set collection_handle = 88435/dsp01qf85nb35s
set eperson = dspace-admin@princeton.edu
set mapfile = import-`date +%s`
set source = /dspace/www/thesis_central/$department/tc_export/Approved/

/dspace/bin/dspace import --add --collection $collection_handle --eperson $eperson --mapfile "import-$department.map" --source /dspace/www/thesis_central/$department/tc_export/Approved
```

