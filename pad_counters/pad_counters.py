""" Command line tool for padding counters in filenames.
    Nick Poberezhnyk
    MIT Licence.
"""
import os
import re
import math
import argparse


parser = argparse.ArgumentParser(
    description="Pad counters of the files in a given directory with zeros"
)

parser.add_argument(
    "path",
    help="path to the directory in which counters should be padded"
)
parser.add_argument(
    "template",
    help="""template by which counters in names will be found without
            extension; for example hello{}world, myfile{}, {}photo,
            where {} is counter position"""
)
parser.add_argument(
    "-e", "--extension",
    help="rename only the files with a given extension"
)
parser.add_argument(
    "-p", "--pad", type=int, choices=range(2, 10),
    help="""length to which numbers should be padded; if not specified
            calculated automatically"""
)
parser.add_argument(
    "-v", "--verbose", action="store_true",
    help="print out names of renamed files"
)

args = parser.parse_args()

if "{}" not in args.template:
    parser.error("Position of the counter should be provided with '{}'")


def filter_by_extension(filenames, extension):
    return [f for f in filenames if f.endswith(f".{extension}")]

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

def get_counter(filename):
    m = re.match(template_to_regex(), filename)
    try:
        return int(m.group(2))
    except IndexError:
        return 0

def get_padding(filenames):
    try:
        max_counter = max(get_counter(f) for f in filenames)
        return math.ceil(math.log10(max_counter + 1))
    except ValueError:
        print("No files matched your template")

def pad_counter(filename, padding):
    m = re.match(template_to_regex(), filename)
    if m is None:
        return filename
    return f"{m.group(1)}{int(m.group(2)):0{padding}}{m.group(3)}"


files_to_rename = os.listdir()
if args.extension:
    files_to_rename = filter_by_extension(files_to_rename, args.extension)
files_to_rename = filter_by_template(files_to_rename)

if args.pad is not None:
    padding = args.pad
else:
    padding = get_padding(files_to_rename)

padded_filenames = [pad_counter(f, padding) for f in files_to_rename]

verbose_output = []

for original, padded in zip(files_to_rename, padded_filenames):
    _, ext = os.path.splitext(original)
    new_name = f"{padded}{ext}"
    os.rename(
        os.path.join(args.path, original),
        os.path.join(args.path, new_name)
    )

    verbose_output.append((original, new_name))

if args.verbose:
    for original, padded in verbose_output:
        print(f"{original} -> {padded}")
