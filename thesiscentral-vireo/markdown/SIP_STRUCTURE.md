# Thesis Central Submission Information Packages (SIPs)

## An Example DSpace Import TAR (Gzip-compressed)
_(This is for the 2020 senior theses submissions within the Mathematics Department, it is distributed as `Mathematics.tgz`)._

The TAR compresses and archives files using the following directory structure:

```
- Approved/
  - submission_8096
    - ANDRONACHE-TEODOR-ANDREI-THESIS.pdf
    - contents
    - dublin_core.xml
    - LICENSE.txt
    - metadata_pu.xml
    - ORIG-ANDRONACHE-TEODOR-ANDREI-THESIS.pdf
  - submission_8113
    - BABUL-SHAZIAAYN-THESIS.pdf
    - contents
    - dublin_core.xml
    - LICENSE.txt
    - metadata_pu.xml
    - ORIG-BABUL-SHAZIAAYN-THESIS.pdf
  - submission_8131
    - [...]
- Mathematics.tsv
- ExcelExport.xlsx
- RestrictionsWithId.xlsx
```

All `submission_[ID]` directory names are generated using the Vireo submission ID for that particular thesis submission. These files otherwise follow the structure detailed in the [Simple Archive Format documentation](https://wiki.lyrasis.org/display/DSDOC5x/Importing+and+Exporting+Items+via+Simple+Archive+Format). Regarding the `contents` file, this indicates that the PDF files are the `ORIGINAL` bundle bitstreams, with the `ORIG-*` PDF files being retained for backup purposes.

The departmental TSV file (`Mathematics.tsv`) is a TSV with the Vireo submission metadata, and is an artifact from the SIP generation process (this is retained primarily for debugging purposes). Similarly, the departmental Excel Spreadsheet (`ExcelExport.xlsx`) is also an artifact, and it contains the Vireo submission metadata originally exported from the Vireo installation. `RestrictionsWithId.xlsx` is a spreadsheet distributed and used between departmental SIP-generation requests, and contains the access permissions for each individual thesis (it, also, is included for reference when debugging import commands).


