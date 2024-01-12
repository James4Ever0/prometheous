# demo logic to generate filesystem hierarchy in markdown

# TODO: diff and line markers shifts based reprocessing: just process the changed part instead of the whole file again
# TODO: calculate code duplication percent across directories, prefer files by timestamp or size

# TODO: show the total stage progress like [Stage 1/4], [Stage 2/4]

# TODO: generate sitemap
# TODO: modify all titles in all pages to contain full project name and project description (more informative titles)
# TODO: print progress info during directory brief generation process

# TODO: provide a brief view to file chunks.
# TODO: provide an AST view (language specific) to file chunks.
# TODO: make our prompt into json to formalize the input structure, and parse the output as json

# language specific shall be built on language agnostic
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source_dir", type=str, required=True)
args = parser.parse_args()

# the only parameter.
source_dir = args.source_dir

assert os.path.exists(source_dir)
assert os.path.isdir(source_dir)
assert os.path.isabs(source_dir)

from collections import defaultdict
import json
import urllib.parse

import sys

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "../"))
from llm import llm_context

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
    return s.strip()


# read metadata.json & data/*.json
# create and read some cache_tree.json, which you may want to include in .gitignore
# produce tree.json
# copy tree.html

import html.entities
html5_escapes = html.entities.html5
html_escape_mapping = {}
for k,v in html5_escapes.items():
    if k.endswith(";"):  html_escape_mapping[v] = "&"+k

def html_escape(s: str):
    ret = ""
    for elem in s:
        if elem in html_escape_mapping.keys():
            ret += html_escape_mapping[elem]
        else:
            ret += elem
    return ret


import hashlib


def hash_key(summary: str):
    enc = summary.strip()
    if enc:
        # Generate a hash for the given summary
        hash_object = hashlib.md5(enc.encode())
        return hash_object.hexdigest()


import tinydb

cache_tree = tinydb.TinyDB(os.path.join(source_dir, "cache_tree.json"))


def generate_file_summary_brief(filepath, summary):
    # Generate a brief for the file based on its summary
    stripped_summary = summary.strip()
    if stripped_summary:
        prompt = f"""
Filepath: {filepath}

Summary:
{stripped_summary}

Brief in 7 words (do not quote your brief, just write it out):
"""
        mhash = hash_key(prompt)
        rec = cache_tree.get(
            (tinydb.Query().hash == mhash) and (tinydb.Query().path == filepath)
        )
        if rec:
            return rec["brief"]
        else:
            init_prompt = """You are a professional brief writer. You can turn long summaries into a single short brief within 7 words. You will be given a filepath, a summary of the file and produce a concise brief that best describes the file.
"""
            with llm_context(init_prompt) as model:
                mbrief = strip_quote(model.run(prompt).strip())
            mdoc = dict(path=filepath, hash=mhash, brief=mbrief)
            cache_tree.upsert(mdoc, cond=tinydb.Query().path == filepath)
            return mbrief
    return ""


def generate_tree_repesentation(
    directory_path: str,
    childrens_mapping: dict[str, set[str]],
    file_briefs: dict[str, str],
    directory_briefs: dict[str, str],
    indent=0,
    briefs=[],
):
    childrens = list(childrens_mapping[directory_path])
    childrens.sort()
    if directory_path == "/":
        name = project_name
    else:
        name = directory_path.strip("/").split("/")[-1]
    mbrief, show = directory_briefs[directory_path]
    mbrief = strip_quote(mbrief)
    briefs.append(
        " " * indent * 4
        + f'- <span hierarchy="{indent}" class="expanded" onclick="toggleVisibility(this)" ><strong class="directory" id="{directory_path}"><code>{html_escape(name)}</code></strong>'
        + ("" if not show else f" <em>{mbrief}</em>")
        + "</span>"
        # " " * indent * 4 + f"- **`{name}`**" + ("" if not show else f" <em>{mbrief}</em>")
    )

    for child in childrens:
        child_name = child.strip("/").split("/")[-1]
        if child.endswith("/"):
            # mbrief, show= directory_briefs[child]
            # briefs.append(
            #     " " * (indent + 1) * 4
            #     + f"- **`{child_name}`**"+("" if not show else f" *{mbrief}*")
            # )
            generate_tree_repesentation(
                child,
                childrens_mapping,
                file_briefs,
                directory_briefs,
                indent + 1,
                briefs,
            )
        else:
            child_link = f"index.html?q={urllib.parse.quote(child)}"
            briefs.append(
                " " * (indent + 1) * 4
                + f'- <a class="file_link" href="{child_link}" id="{child}"><code>{html_escape(child_name)}</code></a> <em>{strip_quote(file_briefs[child])}</em>'
            )

    return briefs



def comment_summarizer(summary_model, comments: list[str],directory_path:str) -> str:
   
    def combine_comments(comment1: str, comment2: str):
        summary_query = f"""
{comment1}

{comment2}

Brief for directory '{directory_path}' in 7 words (do not quote your brief, just write it out):
"""
        ret = summary_model.run(summary_query)
        return ret

    def recursive_combine(comments_list: list[str]):
        if len(comments_list) == 0:
            raise Exception("No comments to combine")
        elif len(comments_list) == 1:
            return comments_list[0]
        elif len(comments_list) % 2 == 0:
            combined = [
                combine_comments(comments_list[i], comments_list[i + 1])
                for i in range(0, len(comments_list), 2)
            ]
        else:
            combined = [
                combine_comments(comments_list[i], comments_list[i + 1])
                for i in range(0, len(comments_list) - 1, 2)
            ]
            combined += [comments_list[-1]]
        return recursive_combine(combined)

    summary = recursive_combine(comments)
    del summary_model
    return summary


def generate_directory_summary_brief(
    directory_path,
    childrens_mapping: dict[str, set[str]],
    file_briefs: dict[str, str],
    directory_briefs={},
):
    # Generate a brief for the directory based on its direct children's briefs
    childrens = list(childrens_mapping[directory_path])
    if len(childrens) == 0:
        raise Exception(f"Directory '{directory_path}' has no children")
    if len(childrens) == 1:
        if childrens[0].endswith("/"):
            generate_directory_summary_brief(
                childrens[0], childrens_mapping, file_briefs, directory_briefs
            )
            mbrief = directory_briefs[childrens[0]][0]
        else:
            mbrief = file_briefs[childrens[0]]
        directory_briefs[directory_path] = (mbrief, False)
    else:
        subprompt_parts = []
        children_briefs = {}
        for child in childrens:
            if child.endswith("/"):
                generate_directory_summary_brief(
                    child, childrens_mapping, file_briefs, directory_briefs
                )
                cbrief = directory_briefs[child][0]
            else:
                cbrief = file_briefs[child]
            children_briefs[child] = cbrief
        candidates = list(children_briefs.items())
        candidates.sort(key=lambda x: x[0])
        for k, v in candidates:
            if not k.endswith("/"):
                mark = "file"
            else:
                mark = "directory"
            relpath = os.path.relpath(k, directory_path)
            it = f"Brief for {mark} '{relpath}': {v}"
            subprompt_parts.append(it)
        subprompt = "\n".join(subprompt_parts)
        prompt = f"""
{subprompt}

Brief for directory '{directory_path}' in 7 words (do not quote your brief, just write it out):
"""
        mhash = hash_key(prompt)

        rec = cache_tree.get(
            (tinydb.Query().hash == mhash) and (tinydb.Query().path == directory_path)
        )
        if rec:
            mbrief = rec["brief"]
        else:
            # TODO: use recursive summarization.
            init_prompt = """You are a professional brief summarizer. You can produce a single short brief within 7 words. You will be given a pair of briefs and produce a concise brief that best describes the directory.
"""
            with llm_context(init_prompt) as model:
                ret = comment_summarizer(model, subprompt_parts,directory_path)
                mbrief = strip_quote(ret.strip())
                # mbrief = strip_quote(model.run(prompt).strip())
            mdoc = dict(path=directory_path, hash=mhash, brief=mbrief)
            cache_tree.upsert(mdoc, cond=tinydb.Query().path == directory_path)
        directory_briefs[directory_path] = (mbrief, True)
    return directory_briefs


file_summaries = {
    v["filepath"]: data[str(v["entry_id"] + 1)]["content"]
    for v in file_mapping.values()
}
# print(file_summaries)

# file_briefs = {k: generate_file_summary_brief(k, v) for k, v in file_summaries.items()}
file_briefs = {}
items_count = len(file_summaries.keys())
print(f"\n>>>> PROCESSING PROGRESS: 0/{items_count}")
counter = 0
for k, v in file_summaries.items():
    file_briefs[k] = generate_file_summary_brief(k, v)
    counter += 1
    print(f"\n>>>> PROCESSING PROGRESS: {counter}/{items_count}")

childrens_mapping = defaultdict(set)

for k in file_summaries.keys():
    print(k)
    split_k = k.split("/")
    print(split_k)  # [dir1, dir2, ... filename]
    # add "/" to the right and left of dir.
    for i in range(len(split_k) - 1):
        parent = "/".join(split_k[: i + 1]) + "/"
        child = parent + split_k[i + 1]
        if i != len(split_k) - 2:  # is directory:
            child += "/"
        print({"i": i, "parent": parent, "child": child, "k": k})
        childrens_mapping[parent].add(child)

# breakpoint()

directory_briefs = generate_directory_summary_brief("/", childrens_mapping, file_briefs)

# now, let's generate the representation.
briefs = generate_tree_repesentation(
    "/", childrens_mapping, file_briefs, directory_briefs
)
# briefs.insert(0,"# Project Structure:")
briefs.insert(
    0,
    f'## Project structure<span hierarchy="0" class="partial-repository-url"> of: {metadata["url"]["partial"]}</span><div style="float: right;"><a title="Document index" style="margin:3.5px;" href="index.html"><i class="bi bi-search"></i></a><a title="Feeling lucky" style="margin:3.5px;" href="tree.html?random=true"><i class="bi bi-dice-3"></i></a><a title="Expand tree" style="margin:3.5px;" href="tree.html?full=true" id="expand-tree"><i class="bi bi-caret-down-square"></i></a></div>',
)
print("=" * 40)
print("\n".join(briefs))


### building

# render README.md into index.html
import markdown
from jinja2 import Template

# Markdown content
markdown_content = "\n".join(briefs)
# Convert Markdown to HTML
html_content = markdown.markdown(markdown_content)

template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tree.html.j2")
css_path = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "github-markdown.css"
)
template = Template(open(template_path, "r").read())
# Render the template with the data
rendered_template = template.render(content=html_content)

print("Template rendered.")

tree_fname = "tree.html"
# Write the template content to a file
with open(os.path.join(source_dir, tree_fname), "w+", encoding="utf-8") as file:
    file.write(rendered_template)

import shutil

shutil.copy(css_path, source_dir)

print(
    f"Markdown converted to HTML and written to {os.path.join(source_dir, tree_fname)}"
)
