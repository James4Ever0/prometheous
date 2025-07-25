# create embedding with ollama
# or use llamaindex instead? it has cache.

# since small local index is enough, we do not need huge vector search database engine.
# if that is the case, we just swap the adapter.

import rich
from langchain.embeddings import OllamaEmbeddings

ollama_emb = OllamaEmbeddings(
    model="openhermes2.5-mistral:latest",
    # model="llama:7b",
)

query = "hello world"
documents = ["hello again", "bye world"]
q_emb = ollama_emb.embed_query(query)
d_emb = ollama_emb.embed_documents(documents)
import numpy as np

rich.print(type(q_emb), np.array(q_emb).shape)  # list
rich.print(type(d_emb), np.array(d_emb).shape)
# <class 'list'>
# (4096,)
# <class 'list'>
# (2, 4096)
