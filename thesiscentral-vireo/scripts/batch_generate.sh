#!/bin/bash

declare -a DEPARTMENTS

DEPARTMENTS=(
 Religion
 Music
 "Creative Writing Program"
 "Woodrow Wilson School"
 "Spanish and Portuguese"
 Sociology
 "Slavic Languages and Literatures"
 Psychology
 "Ops Research and Financial Engineering"
 "Near Eastern Studies"
 "Molecular Biology"
 "Independent Study"
 History
 German
)

VIREO_EXPORTS=(
 ExcelExport\ \(55\).xlsx
 ExcelExport\ \(56\).xlsx
 ExcelExport\ \(57\).xlsx
 ExcelExport\ \(58\).xlsx
 ExcelExport\ \(59\).xlsx
 ExcelExport\ \(60\).xlsx
 ExcelExport\ \(61\).xlsx
 ExcelExport\ \(62\).xlsx
 ExcelExport\ \(63\).xlsx
 ExcelExport\ \(64\).xlsx
 ExcelExport\ \(65\).xlsx
 ExcelExport\ \(66\).xlsx
 ExcelExport\ \(67\).xlsx
 ExcelExport\ \(68\).xlsx
 ExcelExport\ \(69\).xlsx
 ExcelExport\ \(70\).xlsx
 ExcelExport\ \(71\).xlsx
)

generate_sip () {
  DEPT="$1"
  i=$2
  echo "Processing $DEPT with ${VIREO_EXPORTS[$i]}..."

  #mkdir -p "export/$DEPT"
  #cp "thesiscentral-exports/${VIREO_EXPORTS[$i]}" "export/$DEPT/ExcelExport.xlsx"
  #cp export/RestrictionsWithId.xlsx "export/$DEPT/RestrictionsWithId.xlsx"
  #cp export/ImportRestrictions.xlsx "export/$DEPT/ImportRestrictions.xlsx"
  #cp export/AdditionalPrograms.xlsx "export/$DEPT/AdditionalPrograms.xlsx"

  pipenv run python restrictionsFindIds.py --thesis "export/$DEPT/ExcelExport.xlsx" --restrictions "export/$DEPT/RestrictionsWithId.xlsx"
  cd "export/$DEPT"
  unzip DSpaceSimpleArchive.zip
  cd -
  pipenv run python enhanceAips.py --thesis "export/$DEPT/ExcelExport.xlsx" -r "export/$DEPT/RestrictionsWithId.xlsx" --cover_page export/SeniorThesisCoverPage.pdf --add_certs "export/$DEPT/AdditionalPrograms.xlsx" --aips "export/$DEPT" -l INFO
  pipenv run python sortByStatus.py  --thesis "export/$DEPT/ExcelExport.xlsx" --aips "export/$DEPT"

  cd "export/$DEPT"
  rm "$DEPT.tgz"

  tar \
    --create \
    --file="$DEPT.tgz" \
    --gzip \
    --verbose \
    --exclude=DSpaceSimpleArchive/ \
    --exclude=DSpaceSimpleArchive.zip \
    --exclude="$DEPT.tgz" \
    .

  cd -

}

for i in "${!DEPARTMENTS[@]}"; do
  DEPT="${DEPARTMENTS[$i]}"
  generate_sip "$DEPT" $i
done
