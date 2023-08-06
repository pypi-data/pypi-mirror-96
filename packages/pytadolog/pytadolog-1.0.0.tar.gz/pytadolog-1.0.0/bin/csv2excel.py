#!/usr/bin/env python3

"""Console script to convert CSV to Excel file."""
import argparse

from pytadolog import csv2excel


def main():
    """Parse arguments and convert input CSV to Excel file."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="path to csv to convert")
    parser.add_argument(
        "-o",
        "--outpath",
        help="path to output xlsx",
    )
    parser.add_argument(
        "--dropna",
        action="store_true",
        help="drop NaN values in xlsx",
    )
    args = parser.parse_args()
    csv2excel(args.input, args.outpath, args.dropna)
    print("CSV converted to Excel file")


if __name__ == "__main__":
    main()