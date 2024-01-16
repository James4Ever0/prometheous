import hashlib
import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
from langchain.embeddings import OllamaEmbeddings

ollama_emb = OllamaEmbeddings(
    model="openhermes2.5-mistral:latest",
    # model="llama:7b",
)


def hash_doc(enc: str):
    hash_object = hashlib.md5(enc.encode())
    return hash_object.hexdigest()


cache_path = "./docarray_cache"

from docarray import BaseDoc
from docarray.index import HnswDocumentIndex
import numpy as np

from docarray.typing import NdArray


class TextDoc(BaseDoc):
    text: str
    text_hash: str
    embedding: NdArray[4096]


import rich

# create a Document Index
index = HnswDocumentIndex[TextDoc](work_dir=cache_path)


# index your data
docs = ["hello again", "bye world"]
query = "hello world"
# find similar Documents

for it in docs:
    docHash = hash_doc(it)
    index._sqlite_cursor.execute(
        "SELECT text FROM docs WHERE text_hash = ?", (docHash,)
    )
    rows = index._sqlite_cursor.fetchall()
    if len(rows) > 0:
        cached = False
        for row in rows:
            if row[0] == it:
                cached = True
                break
        if cached:
            print("document cached:", it)
            continue

    # result = index.text_search(docHash, search_field="text_hash", limit=1)
    # if result.count == 1:
    #     if result.documents[0].text_hash == docHash:
    #         print("document cached:", it)
    #         continue

    embed = np.array(ollama_emb.embed_query(it))
    docObject = TextDoc(text=it, text_hash=docHash, embedding=embed)
    index.index(docObject)

# breakpoint()

index._sqlite_cursor.execute("SELECT doc_id FROM docs WHERE text LIKE 'hello%'")
# index._sqlite_cursor.execute("SELECT doc_id FROM docs")
# [(423764937781332251,), (955323081996155123,)]
# index._sqlite_cursor.execute("SELECT * FROM docs") # field: doc_id
rows = index._sqlite_cursor.fetchall()
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
