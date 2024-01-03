from rich.text import Text
from rich.console import Console
import datetime

# color from:
from rich.color import ANSI_COLOR_NAMES

from collections import defaultdict

console = Console()
from rich.tree import Tree
from rich import print
import json
import os
import humanize

error_map = defaultdict(list)


def size_to_readable_string(size: int):
    return humanize.naturalsize(size)


GREY = "bright_black"

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--full", help="full tree", type=str, required=True)
parser.add_argument("--selected", help="selected tree", type=str, required=True)
parser.add_argument("--basepath", help="path to the base", type=str, required=True)
args = parser.parse_args()

full_json = args.full
selected_json = args.selected
basepath = args.basepath

tree_data = json.load(open(full_json))
selected_json = json.load(open(selected_json))  # could be different.

size_map = {}
selected_keys = []


# Add the tree contents recursively
def add_tree_contents(parent, contents, basedir=".", basemap={}):
    for item in contents:
        if item["type"] == "directory":
            # subtree = parent.add(f"[bold]{item['name']}")
            subtree = parent.add(
                Text.assemble((item["name"], "bold")),
                style=GREY,
                guide_style=GREY,
            )
            basemap[os.path.join(basedir, item["name"] + "/")] = subtree
            dirfs = 0
            for fs in add_tree_contents(
                subtree,
                item.get("contents", []),
                os.path.join(basedir, item["name"]),
                basemap,
            ):
                dirfs += fs
                yield fs
            size_map[os.path.join(basedir, item["name"] + "/")] = dirfs
        else:  # file
            # subtree = parent.add(item['name'])
            filesize = os.path.getsize(
                os.path.join(basepath, os.path.join(basedir, item["name"]))
            )
            size_map[os.path.join(basedir, item["name"])] = filesize
            filesize_human = size_to_readable_string(filesize)
            subtree = parent.add(f"[{filesize_human}] " + item["name"], style=GREY)
            basemap[os.path.join(basedir, item["name"])] = subtree
            yield filesize


def dirsplit(path):
    if path.endswith("/"):
        path = path[:-1]
    return os.path.split(path)


def patch_missing_files(path, basemap):
    subpath, filename = dirsplit(path)
    # breakpoint()
    if basemap.get(path) is None:
        subtree = patch_missing_files(subpath + "/", basemap)
        subsubtree = subtree.add(filename, style="white", guide_style="white")
        # print(filename)
        basemap[path] = subsubtree
        return subsubtree
    else:
        return basemap.get(path)


def set_path_to_white(path, basemap):
    subtree = patch_missing_files(path, basemap)
    subtree.style = "white"
    subtree.guide_style = "white"
    return subtree


selected_dirs = []

line_map = {}


# can have missing files.
def iterate_all_keys(contents, basemap, basedir="."):
    for item in contents:
        if item["type"] == "directory":
            subpaths = item.get("contents", [])
            if subpaths:
                dirlc = 0
                for lc in iterate_all_keys(
                    subpaths, basemap, os.path.join(basedir, item["name"])
                ):
                    dirlc += lc
                    yield lc
                if dirlc != 0:
                    selected_dirs.append(os.path.join(basedir, item["name"] + "/"))
                    set_path_to_white(
                        os.path.join(basedir, item["name"] + "/"), basemap
                    )
                    line_map[os.path.join(basedir, item["name"] + "/")] = dirlc
        else:  # file
            # breakpoint()
            selected_keys.append(os.path.join(basedir, item["name"]))
            linecount = read_file_and_get_line_count(
                os.path.join(basepath, os.path.join(basedir, item["name"]))
            )
            line_map[os.path.join(basedir, item["name"])] = linecount
            subtree = set_path_to_white(os.path.join(basedir, item["name"]), basemap)
            error = True
            if linecount == 0:
                label = "Empty"
            elif linecount == -1:
                label = "Missing"
            elif linecount == -2:
                label = "Error"
            else:
                label = f"{linecount} L"
                error = False
            if error:
                error_map[os.path.join(basedir, item["name"])].append(label)
            else:
                yield linecount
            subtree.label = f"[{label}] " + item["name"]


def read_file_and_get_line_count(filepath: str):
    if not os.path.exists(filepath):
        return -1
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
            return len(lines)
    except:
        return -2


selected_keys = []


def get_selected_keys(tree_data, basemap):
    iterate_all_keys(tree_data[0].get("contents", []), basemap)
    return selected_keys


tree = Tree("agi_computer_control")
# tree = Tree("agi_computer_control", style=GREY, guide_style=GREY)
root = tree_data[0]  # Assuming the first item in the JSON is the root directory
mymap = {}
total_size = sum(add_tree_contents(tree, root.get("contents", []), basemap=mymap))
total_lines = sum(iterate_all_keys(selected_json[0].get("contents", []), mymap))
# Print the tree
tree.label = Text.assemble(
    (
        (
            f"[{total_lines} L] "
            if total_lines != 0
            else f"[{size_to_readable_string(total_size)}] "
        )
        + tree.label,
        "magenta",
    )
)


def estimate_time_from_lines(line_count: int):
    seconds = (line_count / 10) * 100
    return humanize.naturaltime(datetime.timedelta(seconds=seconds)).split(" ago")[0]


for k, v in mymap.items():
    if k.endswith("/"):
        _, name = dirsplit(k)
        if k in selected_dirs:
            v.label = f"[{line_map[k]} L] " + name
            # v.label = f"[{estimate_time_from_lines(line_map[k])}] "+ name
        else:
            v.label = f"[{size_to_readable_string(size_map[k])}] " + name

console = Console()
console.print(tree)

# total_size = sum(size_map.values())
selected_size = sum(size_map[k] for k in selected_keys)

# make mapping between displayed tree and actual tree
print(
    dict(
        total=size_to_readable_string(total_size),
        selected=size_to_readable_string(selected_size),
    )
)

# total_lines = sum(line_map.values())
print(dict(selected_lines=humanize.intword(total_lines) + " lines"))
processing_time = estimate_time_from_lines(total_lines)
print(dict(processing_time=processing_time))

total_size_by_suffix = defaultdict(int)

for k, v in size_map.items():
    suffix = os.path.split(k)[1].split(".")[-1]
    total_size_by_suffix[suffix] += v
lines_by_suffix = defaultdict(int)

for k in selected_keys:
    suffix = os.path.split(k)[1].split(".")[-1]
    v = line_map[k]
    lines_by_suffix[suffix] += v
print(
    dict(
        total={k: size_to_readable_string(v) for k, v in total_size_by_suffix.items()},
        # total=set(os.path.split(it)[1].split(".")[-1] for it in size_map.keys()),
        selected={
            k: humanize.intword(v) + " lines" for k, v in lines_by_suffix.items()
        },
    )
)
print("error:", {k: len(v) for k, v in error_map.items()})
# print(mymap)
