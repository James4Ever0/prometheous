# responsible for turning everything into embeddings.

# responsible for caching, index wirings.

# code chunk with title, chunk description with title

# code document chunks, folder document chunks

# latest code chunks -> embeddings
# folder/file summary hash -> latest document chunks -> document chunk hash -> embeddings

import os
import argparse

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from tinydb import TinyDB

class FileSummary(BaseModel):
    file_hash: str
    summary: str

class FolderSummary(BaseModel): # this is not generated. do it now.
    folder_hash: str
    summary: str

textSpliter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
)
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

metadata = json.loads(open(os.path.join(source_dir, "metadata.json"), "r").read())
title_metadata = json.loads(open(os.path.join(source_dir, "metadata_title.json"), "r").read())

file_mapping = metadata["file_mapping"]
split_count = metadata["split_count"]
project_name = metadata["project_name"]

title_split_count = title_metadata["split_count"]

data = {}
title_data = {}

for i in range(split_count):
    new_data = json.loads(open(os.path.join(source_dir, f"data/{i}.json"), "r").read())
    data.update(new_data)

for i in range(title_split_count):
    new_data = json.loads(open(os.path.join(source_dir, f"data/titles/{i}.json"), "r").read())
    title_data.update(new_data)

def strip_quote(s: str):
    if s[0] == s[-1]:
        if s[0] in ['"', "'"]:
            return s[1:-1].strip()
    return s.strip().strip(".")


file_summary_dict = {}
file_comment_dict = {}
file_code_dict = {}

import hashlib

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from langchain.embeddings import OllamaEmbeddings

ollama_emb = OllamaEmbeddings(
    model="openhermes2.5-mistral:latest",
    # model="llama:7b",
)

def hash_doc(enc: str):
    hash_object = hashlib.md5(enc.encode())
    return hash_object.hexdigest()


from docarray import BaseDoc
from docarray.index import HnswDocumentIndex # type: ignore
import numpy as np

from docarray.typing import NdArray


class CodeCommentChunk(BaseDoc):
    code: str
    comment: str
    title: str
    chunk_hash: str
    file_hash: str
    embedding: NdArray[4096] # type:ignore


class FileDocumentChunk(BaseDoc):
    file_hash: str
    chunk: str
    embedding: NdArray[4096] # type:ignore


class FolderDocumentChunk(BaseDoc):
    folder_hash: str
    chunk: str
    embedding: NdArray[4096] # type:ignore


# import rich

cache_path_base = os.path.join(source_dir, "vector_cache")
document_cache_path_bash = os.path.join(cache_path_base, "document")

if not os.path.exists(cache_path_base):
    os.mkdir(cache_path_base)
if not os.path.exists(document_cache_path_bash):
    os.mkdir(document_cache_path_bash)

# create a Document Index
comment_index = HnswDocumentIndex[CodeCommentChunk](
    work_dir=os.path.join(cache_path_base, "comment")
)
file_document_index = HnswDocumentIndex[FileDocumentChunk](
    work_dir=os.path.join(document_cache_path_bash, "file")
)
folder_document_index = HnswDocumentIndex[FolderDocumentChunk](
    work_dir=os.path.join(document_cache_path_bash, "folder")
)

for it in docs:
    docHash = hash_doc(it)
    comment_index._sqlite_cursor.execute(
        "SELECT text, doc_id FROM docs WHERE text_hash = ?", (docHash,)
    )
    rows = comment_index._sqlite_cursor.fetchall()
    if len(rows) > 0:
        cached = False
        for row in rows:
            if row[0] == it:
                cached = True
                doc_id = row[1]
                break
        if cached:
            print("document cached:", it)
            continue

    embed = np.array(ollama_emb.embed_query(it))
    docObject = TextDoc(text=it, text_hash=docHash, embedding=embed)
    index.index(docObject)

comment_index._sqlite_cursor.execute("SELECT doc_id FROM docs WHERE text LIKE 'hello%'")
rows = comment_index._sqlite_cursor.fetchall()
# print(rows)
hashed_ids = set(it[0] for it in rows)
# hashed_ids = set(str(it[0]) for it in rows)
# print(hashed_ids)
ans = index._search_and_filter(
    np.array(ollama_emb.embed_query(query)).reshape(1, -1),
    limit=10,
    search_field="embedding",
    hashed_ids=hashed_ids,
)
rich.print("ans:", ans)
# breakpoint()

# hnswlib ids: [955323081996155123, 423764937781332251]
results, scores = index.find(
    ollama_emb.embed_query(query), limit=10, search_field="embedding"
)
rich.print(results, scores)
