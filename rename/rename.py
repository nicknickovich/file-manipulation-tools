""" Command line tool for renaming multiple files with similar filenames.
    Nick Poberezhnyk
    MIT Licence.
"""
import os
import re
import argparse


parser = argparse.ArgumentParser(
    description="Rename multiple files in a directory"
)

parser.add_argument(
    "path", type=str,
    help="path to the directory in which files should be renamed"
)
parser.add_argument(
    "-p", "--prefix", type=str, default="",
    help="part of the name before counter"
)
parser.add_argument(
    "-s", "--suffix", type=str, default="",
    help="part of the name after counter"
)
parser.add_argument(
    "-e", "--extension", type=str,
    help="""rename only the files with a given extension,
            it is recommended this option is always specified"""
)
parser.add_argument(
    "-f", "--first", type=int, default=1,
    help="start counting from a given number, default value is 1"
)
parser.add_argument(
    "-t", "--template",
    help="""template by which filenames will be filtered; position of
            the counter should be marked by '{}'"""
)
parser.add_argument(
    "--pad", type=int, default=2, choices=range(2, 10),
    help="""set the width of a zero padded counter in renamed files,
            default is 2"""
)
parser.add_argument(
    "-v", "--verbose", action="store_true",
    help="print out names of renamed files"
)

args = parser.parse_args()

if not (args.prefix or args.suffix):
    parser.error("Prefix and/or suffix must be provided")


def filter_by_extension(filenames):
    return [f for f in filenames if f.endswith(f".{args.extension}")]

def filter_by_template(filenames):
    filtered_filenames = []
    name_regex = template_to_regex()
    for filename in filenames:
        name, _ = os.path.splitext(filename)
        if re.fullmatch(name_regex, name):
            filtered_filenames.append(filename)
    return filtered_filenames

def template_to_regex():
    m = re.fullmatch(r"(.*)({})(.*)", args.template)
    if m is None:
        return ""
    return re.compile(fr"({m.group(1)})(\d+)({m.group(3)})")


files_to_rename = os.listdir()
if args.extension:
    files_to_rename = filter_by_extension(files_to_rename)
if args.template:
    files_to_rename = filter_by_template(files_to_rename)

verbose_output = []

for index, item in enumerate(sorted(files_to_rename), start=args.first):
    _, ext = os.path.splitext(item)
    new_name = f"{args.prefix}{index:0{args.pad}}{args.suffix}{ext}"
    os.rename(
        os.path.join(args.path, item),
        os.path.join(args.path, new_name)
    )
    verbose_output.append((item, new_name))

if args.verbose:
    for original, renamed in verbose_output:
        print(f"{original} -> {renamed}")
