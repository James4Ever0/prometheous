# TODO: ensure "docs" in the .fdignore

import argparse
import os

parser = argparse.ArgumentParser(
    description='Make sure .fdignore file under base directory contains "docs" entry'
)
parser.add_argument("-b", "--basedir", help="base directory", required=True, type=str)
args = parser.parse_args()
basedir = args.basedir

assert os.path.isdir(basedir)
assert os.path.isabs(basedir)
assert os.path.exists(basedir)

fdignore_path = os.path.join(basedir, ".fdignore")
lines = []
if os.path.exists(fdignore_path):
    with open(fdignore_path, "r") as f:
        content = f.read()
        lines = content.split("\n")

if "docs" not in lines:
    lines.append("docs")
    with open(fdignore_path, "w+") as f:
        f.write("\n".join(lines))
