# generate title

# create /cache_title.json, /metadata_title.json, /data/titles/<number>.json

# hash by comment, cache by path identifier and comment hash

# identify those identical comments (file that only has one segment), only give title to file not segment

# only display title if exists

import os
import argparse
from re import L

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source_dir", type=str, required=True)
args = parser.parse_args()

# the only parameter.
source_dir = args.source_dir

assert os.path.exists(source_dir)
assert os.path.isdir(source_dir)
assert os.path.isabs(source_dir)

import json

import sys

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
from llm import llm_context
from slice_utils import split_dict_into_chunks

metadata = json.loads(open(os.path.join(source_dir, "metadata.json"), "r").read())

file_mapping = metadata["file_mapping"]
split_count = metadata["split_count"]
project_name = metadata["project_name"]

data = {}
for i in range(split_count):
    new_data = json.loads(open(os.path.join(source_dir, f"data/{i}.json"), "r").read())
    data.update(new_data)


def strip_quote(s: str):
    if s[0] == s[-1]:
        if s[0] in ['"', "'"]:
            return s[1:-1].strip()
    return s.strip().strip(".")


from tinydb import TinyDB, Query

cache_title = TinyDB(os.path.join(source_dir, "cache_title.json"))

title_split_dir = os.path.join(source_dir, "data/titles")
metadata_title_path = os.path.join(source_dir, "metadata_title.json")
import shutil

if not os.path.exists(title_split_dir):
    os.makedirs(title_split_dir)
else:
    shutil.rmtree(title_split_dir)
    os.makedirs(title_split_dir)

if not os.path.isdir(title_split_dir):
    raise Exception(
        f"'{title_split_dir}' (where splited titles stored) must be a directory"
    )

# structure:
# [filepath] [summary] [code] [comment] ...

title_data = {}

file_mapping_detail = {}
data_count = len(data.keys())

import hashlib


def hash_key(summary: str):
    enc = summary.strip()
    if enc:
        # Generate a hash for the given summary
        hash_object = hashlib.md5(enc.encode())
        return hash_object.hexdigest()


def ask_llm_for_title(path: str, comment: str):
    init_prompt = """You are a professional title writer. You can write a concise, conclusive and meaningful title within 3 to 7 words. You will be given a piece of content, a path that refers to the content and produce a single title.
"""
    with llm_context(init_prompt) as model:
        prompt = f"""Content:
{comment}

Path of the content: {path}

Title within 3 to 7 words (do not quote the title, just write it out):
"""
        ret = model.run(prompt).strip()
        ret = strip_quote(ret)
    return ret


def generate_title_and_update_to_result(
    path: str, comment: str, result_dict: dict[str, str]
):
    comment_hash = hash_key(comment)
    doc = cache_title.get((Query().hash == comment_hash) and (Query().path == path))
    if doc:
        mtitle = doc["title"]
    else:
        mtitle = ask_llm_for_title(path, comment)
        cache_title.upsert(
            dict(path=path, hash=comment_hash, title=mtitle), cond=Query().path == path
        )
    result_dict[path] = mtitle


for k, v in file_mapping.items():
    # end_id is exclusive.
    if str(int(k) + 1) in file_mapping.keys():
        end_id = int(file_mapping[str(int(k) + 1)]["entry_id"])
    else:
        end_id = data_count
    file_mapping_detail[k] = {
        "filepath": v["filepath"],
        "span": {"start": int(v["entry_id"]), "end": end_id},
    }
file_count = len(file_mapping.keys())
print(f"\n>>>> PROCESSING PROGRESS: 0/{file_count}")

for i in range(file_count):
    try:
        it = file_mapping_detail[str(i)]
        start, end = it["span"]["start"], it["span"]["end"]
        split_count = (end - start - 2) / 2
        split_count = int(split_count)
        # generate for file summary title first.
        generate_title_and_update_to_result(
            data[str(start)]["content"], data[str(start + 1)]["content"], title_data
        )
        if split_count == 1:  # only generate for file summary
            continue
        else:
            # generate for splits
            for j in range(split_count):
                generate_title_and_update_to_result(
                    data[str(start + 2 + j * 2)]["location"],
                    data[str(start + 3 + j * 2)]["content"],
                    title_data,
                )
    finally:
        print(f"\n>>>> PROCESSING PROGRESS: {i+1}/{file_count}")

# split and store file summaries.

print("Spliting and storing titles...")
title_split_count = 0
import json

for i, chunk in enumerate(split_dict_into_chunks(title_data, 300)):
    title_split_count += 1
    with open(os.path.join(title_split_dir, f"{i}.json"), "w+") as f:
        f.write(json.dumps(chunk, indent=4, ensure_ascii=False))
print("Storing title metadata...")
with open(metadata_title_path, "w+") as f:
    f.write(json.dumps(dict(split_count=title_split_count)))
print("Finished title generation.")
