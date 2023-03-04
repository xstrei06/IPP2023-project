import argparse
import os
import sys
def valid_file(filename):
    if not os.path.isfile(filename):
        raise argparse.ArgumentTypeError(f"{filename} is not a valid file")
    return filename

parser = argparse.ArgumentParser(usage='interpret.py [--help] [--source=file] [--input=file]', add_help=False, formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('--help', action="store_true", help='Display help message and exit (if no other arguments are specified).')
parser.add_argument("--source", metavar="file", type=valid_file, required=False, help="XML file to be interpreted (if not specified, reads from stdin)")
parser.add_argument("--input", metavar="file", type=valid_file, required=False,
                    help="Program input file (if not specified, reads from stdin)")

parser.epilog = "Note: At least one of the arguments --source=file or --input=file must be specified."

args = parser.parse_args()

if args.help and len(sys.argv) > 2:
    parser.error("Invalid argument combination.")
elif args.help:
    parser.print_help()
    sys.exit(0)

print(args)