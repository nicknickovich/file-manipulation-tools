""" Command line tool for deleting multiple files/directories.
    Nick Poberezhnyk
    MIT Licence.
"""
import os
import re
import argparse
import shutil


parser = argparse.ArgumentParser(
    description="Delete multiple files/directories by given regexp"
)

parser.add_argument(
    "regexp",
    help="Regular expression that will be used to search for files to remove"
)
parser.add_argument(
    "-r", "--recursive", action="store_true",
    help="""Search for files in directories recursively. For directories
            this is always true"""
)
parser.add_argument(
    "-d", "--dirs", action="store_true",
    help="Indicates that objects for removal should be directories"
)

args = parser.parse_args()


base_dir = os.getcwd()
template = re.compile(args.regexp)

paths_to_remove = []

for directory in os.walk(base_dir):
    dirpath, dirnames, filenames = directory
    if args.dirs:
        for dirname in dirnames:
            if re.fullmatch(template, dirname):
                paths_to_remove.append(os.path.join(dirpath, dirname))
    elif args.recursive:
        for filename in filenames:
            if re.fullmatch(template, filename):
                paths_to_remove.append(os.path.join(dirpath, filename))

if not args.recursive and not args.dirs:
    for entry in os.scandir(base_dir):
        if entry.is_file() and re.fullmatch(template, entry.name):
            paths_to_remove.append(entry.path)

valid_answers = {
    "n": "no",
    "no": "no",
    "y": "yes",
    "yes": "yes"
}

print(f"The following {'directories' if args.dirs else 'files'} will be removed")
for path in paths_to_remove:
    print(path)

print("Are you sure you want to continue? yes/no")
answer = input().lower()
while answer not in valid_answers:
    print("Type yes or no")
    answer = input().lower()

if valid_answers[answer] == "no":
    parser.exit("Removing aborted")
else:
    if args.dirs:
        for path in paths_to_remove:
            shutil.rmtree(path, ignore_errors=True)
    else:
        for path in paths_to_remove:
            os.remove(path)
    print("Done")
