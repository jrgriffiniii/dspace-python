# Importing DataSpace Items

## Importing Thesis Central (Vireo) submissions into DataSpace (DSpace)
Thesis Central submissions are organized by academic departments.

## Preparing a local environment
```bash
git clone https://github.com/pulibrary/dspace-python
pyenv 2.7.5
pipenv shell
cd thesiscentral-vireo/dataspace/python
```

## Exporting from Thesis Central
Users must export Excel Spreadsheet after selecting a department from thesis-central.princeton.edu.

[screenshot]

## Applying Restrictions

One must then export the submission restrictions from the University Sharepoint
provided by the Office of the Registrar (please see URL).

Then, one must add an `ID` column to this exported spreadsheet:

[screenshot]

## Building DSpace Submission Information Packages [SIPs]

Create directory for the department:

```bash
mkdir export/$department
cp ~/Download/thesis_central_export.xlsx export/$department/ExcelExport.xlsx
cp ~/Download/dspace_simple_archive.zip export/$department/
pipenv run prepare-to-dataspace export/$department
```

### Multi-Author Submissions

```bash
cd export/Multi-Author
check_all_approved

combine_all_approved
check_after_combine
```

#### Transfer the SIPs to the server

```bash
export department="Multi-Author"
(cd export; tar cfz $department.tgz ./$department)
scp export/$department.tgz monikasu@arizona.princeton.edu:/scratch/monikasu/$department.tgz
ssh monikasu@arizona.princeton.edu chmod o+r /scratch/monikasu/$dept.tgz
```

## Import to DataSpace

From the DataSpace server environment, please invoke the following:

```bash
ssh -J libvijrg@epoxy.princeton.edu libvijrg@dataspace.princeton.edu
cd ~/thesiscentral-vireo/dataspace/import
./unwrap

# just cut and paste the desrived tgz file from the prompt
# test access at https://dataspace.princeton.edu/www/thesis_central/

# then import to dspace - follow prompts

./import
```

