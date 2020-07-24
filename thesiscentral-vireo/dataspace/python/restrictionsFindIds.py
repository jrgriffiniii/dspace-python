"""
A CLI wrapper for match_ids, a function that looks through the export_file to
 see if there are any submissions that match in restrictions_file. It exports
 the department's restricted submissions to output_file.

The default inputs and outputs match the directory structure proposed for the
 current workflow; however, they can be overwritten by command line arguments.

An example shell command:

python restrictionsFindIds.py --department English

"""

import pandas as pd
import os
import argparse

class ArgParser(argparse.ArgumentParser):
    @staticmethod
    def create():
        description = """A CLI wrapper for match_ids, a function that looks through the export_file to
 see if there are any submissions that match in restrictions_file. It exports
 the department's restricted submissions to output_file."""

        parser = ArgParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('--department', "-d", required=True, help="The department to search for IDs")
        parser.add_argument("--thesis", "-t", required=False, help="Excel export file from vireo", default=None)
        parser.add_argument("--restrictions", "-r", required=False, help="Access restrictions spreadsheet", default='downloads/Restrictions.xlsx')
        parser.add_argument("--output", "-o", required=False, help="The output spreadsheet", default=None)
        return parser

    def parse_args(self):
        args= argparse.ArgumentParser.parse_args(self)
        return args

def match_ids(department,
        restrictions_file='downloads/Restrictions.xlsx',
        output_file='ImportRestrictions.xlsx',
        export_file=None
    ):
    """Look through the export_file to see if there are any submissions that
     match in restrictions_file. Export the department's restricted submissions
     to output_file.
    """

    def vireoName(r_name):
        splts = r_name.split();
        return '%s, %s' % (splts[-1], splts[0])

    def raise_choice(id_list):
        if len(id_list) == 0:
            return None
        if len(id_list) == 1:
            return str(id_list[0])
        else:
            # TODO: Check if titles or departments match before raising error
            print(id_list)
            raise ValueError(
                "Two students with the same name exist." +
                " You'll need to manually determine their PUID."
            )

    export_file = 'downloads/{}/ExcelExport.xlsx'.format(department) if export_file is None else export_file
    output_file = 'export/{}/RestrictionsWithId.xlsx'.format(department) if output_file is None else output_file

    # import restrictions and export spreadsheets
    df_r = pd.read_excel(restrictions_file)
    df_e = pd.read_excel(export_file)

    # Link the IDs between the two spreadsheets
    df_r['ID'] = [df_e[df_e['Student name'] == vireoName(r['Submitted By'])]['Student ID'].tolist() for i, r in df_r.iterrows()]
    df_r['ID'] = df_r['ID'].apply(raise_choice)

    # Drop all rows that don't contain IDs and output new spreadsheet
    df_r = df_r[~pd.isna(df_r['ID'])]
    df_r.to_excel(output_file, index=False)

def main():
    parser = ArgParser.create()
    args = parser.parse_args()

    match_ids(args.department,
        restrictions_file=args.restrictions,
        output_file=args.output,
        export_file=args.thesis
    )

if __name__ == "__main__":
    main()