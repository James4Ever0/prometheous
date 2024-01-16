from llama_index import Document
from llama_index.embeddings import OllamaEmbedding  # OpenAIEmbedding
from llama_index.text_splitter import SentenceSplitter
from llama_index.extractors import TitleExtractor
from llama_index.ingestion import IngestionPipeline
from llama_index.llms import Ollama

from llama_index.storage.docstore import SimpleDocumentStore

# from llama_index.ingestion.cache import SimpleCache

# create the pipeline with transformations
embed = OllamaEmbedding(model_name="openhermes2.5-mistral:latest")
llm = Ollama(model="openhermes2.5-mistral:latest")
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=25, chunk_overlap=0),
        TitleExtractor(llm=llm),
        embed,
    ],
    docstore=SimpleDocumentStore() # do it if you want load/persist to work properly.
)
import os

loadpath = "./pipeline_storage"
if os.path.exists(loadpath):
    pipeline.load(persist_dir = loadpath)
# run the pipeline
nodes = pipeline.run(documents=[Document.example()]) # return newly added nodes.
import rich

rich.print(nodes)
pipeline.persist(persist_dir = loadpath) # not persisting document.
