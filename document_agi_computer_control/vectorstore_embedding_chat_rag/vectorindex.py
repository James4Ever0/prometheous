# responsible for turning everything into embeddings.

# responsible for caching, index wirings.

# code chunk with title, chunk description with title

# code document chunks, folder document chunks

# latest code chunks -> embeddings
# folder/file summary hash -> latest document chunks -> document chunk hash -> embeddings

import os
import argparse

os.environ["OPENAI_API_KEY"] = "any"
os.environ["OPENAI_API_BASE"] = "http://0.0.0.0:8000"
os.environ["BETTER_EXCEPTIONS"] = "1"

from langchain.text_splitter import RecursiveCharacterTextSplitter
from pydantic import BaseModel
from tinydb import TinyDB


class FileSummary(BaseModel):
    file_hash: str
    summary: str


class FolderSummary(BaseModel):  # this is not generated. do it now.
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
from llm import llm_context

cache_path_base = os.path.join(source_dir, "vector_cache")
document_cache_path_bash = os.path.join(cache_path_base, "document")

if not os.path.exists(cache_path_base):
    os.mkdir(cache_path_base)
if not os.path.exists(document_cache_path_bash):
    os.mkdir(document_cache_path_bash)
folder_summary_db = TinyDB(os.path.join(cache_path_base, "folder_summaries.json"))

metadata = json.loads(open(os.path.join(source_dir, "metadata.json"), "r").read())

title_metadata = json.loads(
    open(os.path.join(source_dir, "metadata_title.json"), "r").read()
)

file_mapping = metadata["file_mapping"]
split_count = metadata["split_count"]
project_name = metadata["project_name"]

title_split_count = title_metadata["split_count"]

data = {}
title_data = {}

# file_title_indices = []
file_summary_indices = [v["entry_id"] + 1 for v in file_mapping.values()]

for i in range(split_count):
    new_data = json.loads(open(os.path.join(source_dir, f"data/{i}.json"), "r").read())
    data.update(new_data)

for i in range(title_split_count):
    new_data = json.loads(
        open(os.path.join(source_dir, f"data/titles/{i}.json"), "r").read()
    )
    title_data.update(new_data)
# breakpoint()


def strip_quote(s: str):
    if s[0] == s[-1]:
        if s[0] in ['"', "'"]:
            return s[1:-1].strip()
    return s.strip().strip(".")


file_summary_dict = {}
file_hash_dict = {}

file_chunk_comment_dict = {}
file_chunk_code_dict = {}

import hashlib


def hash_doc(enc: str):
    hash_object = hashlib.md5(enc.encode())
    return hash_object.hexdigest()


code_and_comment_list = []

for k, v in data.items():
    if v["type"] == "code":
        code_elem = v
        comment_elem = data[str(int(k) + 1)]

        code_content = v["content"]
        comment_content = comment_elem["content"]
        location = v["location"]
        code_and_comment_list.append(
            dict(code=code_content, comment=comment_content, location=location)
        )
        # chunk_hash = hash_doc(code_content)


os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from langchain.embeddings import OllamaEmbeddings

ollama_emb = OllamaEmbeddings(
    model="openhermes2.5-mistral:latest",
    # model="llama:7b",
)


from docarray import BaseDoc
from docarray.index import HnswDocumentIndex  # type: ignore
import numpy as np

from docarray.typing import NdArray


class CodeCommentChunk(BaseDoc):
    code: str
    comment: str
    location: str
    chunk_hash: str
    embedding: NdArray[4096]  # type:ignore


class FileDocumentChunk(BaseDoc):
    file_hash: str
    chunk: str
    embedding: NdArray[4096]  # type:ignore


class FolderDocumentChunk(BaseDoc):
    folder_hash: str
    chunk: str
    embedding: NdArray[4096]  # type:ignore


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

comment_index_ids = []
import progressbar

for it in progressbar.progressbar(code_and_comment_list, prefix="code and comments:"):
    chunk_hash = hash_doc(it["code"])
    comment_index._sqlite_cursor.execute(
        "SELECT location, doc_id FROM docs WHERE chunk_hash = ?", (chunk_hash,)
    )
    rows = comment_index._sqlite_cursor.fetchall()
    if len(rows) > 0:
        cached = False
        for row in rows:
            if row[0] == it["location"]:
                cached = True
                doc_id = row[1]
                comment_index_ids.append(doc_id)
                break
        if cached:
            print("document cached:", str(it)[:50]+ '...}')
            continue

    code_and_comment = f"""Code:

{it['code']}

Comment:

{it['comment']}
"""

    embed = np.array(ollama_emb.embed_query(code_and_comment))
    docObject = CodeCommentChunk(
        **it, chunk_hash=chunk_hash, embedding=embed
    )  # type:ignore

    doc_id = comment_index._to_hashed_id(docObject.id)
    comment_index_ids.append(doc_id)
    comment_index.index(docObject)

# comment_index._sqlite_cursor.execute("SELECT doc_id FROM docs WHERE text LIKE 'hello%'")
# rows = comment_index._sqlite_cursor.fetchall()
# # print(rows)
# hashed_ids = set(it[0] for it in rows)
# # hashed_ids = set(str(it[0]) for it in rows)
# print(hashed_ids)


def print_and_return(content: str):
    return content + "\n"


if __name__ == "__main__":
    # query for code & embedding index
    query = input("query for code & embedding index:\n")
    ans = comment_index._search_and_filter(
        np.array(ollama_emb.embed_query(query)).reshape(1, -1),
        limit=3,
        # limit=10,
        search_field="embedding",
        hashed_ids=set(comment_index_ids),
    )
    print("ans:", ans)

    context = ""

    for it in ans.documents[0]:
        location = it.location
        file_location = location.split(":")[0]
        context += print_and_return("-" * 10)
        context += print_and_return("Location:")
        context += print_and_return(location)
        # context += print_and_return("Title:")
        # context += print_and_return(title_data.get(location, title_data[file_location]))
        context += print_and_return("Comment:")
        context += print_and_return(it.comment)
        context += print_and_return("Code:")
        context += print_and_return(it.code)
    init_prompt = """You are a helpful assistant who can answer questions based on relevant context about a specific code project. Please answer the user query according to the context.
Assume the reader does not know anything about how the project is strucuted or which folders/files are provided in the context.
Do not reference the context in your answer. Instead use the context to inform your answer.
If you don't know the answer, just say "Hmm, I'm not sure." Don't try to make up an answer.
Your answer should be at least 100 words and no more than 300 words.
Do not include information that is not directly relevant to the question, even if the context includes it.
"""
    with llm_context(init_prompt, temperature=0.2) as model:
        model.run(
            f"Context:\n{context}\nUser query: {query}\nRespond in Markdown format:\n"
        )
