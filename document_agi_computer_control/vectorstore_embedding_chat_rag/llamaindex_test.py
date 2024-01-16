from llama_index import Document
from llama_index.embeddings import OllamaEmbedding  # OpenAIEmbedding
from llama_index.text_splitter import SentenceSplitter
from llama_index.extractors import TitleExtractor
from llama_index.ingestion import IngestionPipeline
from llama_index.llms import Ollama

from llama_index.storage.docstore import SimpleDocumentStore
import os

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from llama_index import VectorStoreIndex, ServiceContext, LLMPredictor
from llama_index.vector_stores import DocArrayHnswVectorStore

# from llama_index.vector_stores import SimpleVectorStore

# from llama_index.ingestion.cache import SimpleCache


vector_store = DocArrayHnswVectorStore("storage",dim = 4096)

# create the pipeline with transformations
# if os.path.exists("./storage"):
#     vector_store = SimpleVectorStore.from_persist_dir()
# else:
#     vector_store = SimpleVectorStore(stores_text=True)
# vector_store.stores_text=True
embed = OllamaEmbedding(model_name="openhermes2.5-mistral:latest")
llm = Ollama(model="openhermes2.5-mistral:latest")
pipeline = IngestionPipeline.construct(
    transformations=[
        SentenceSplitter(chunk_size=25, chunk_overlap=0),
        TitleExtractor(llm=llm),
        embed,
    ],
    docstore=SimpleDocumentStore(),  # do it if you want load/persist to work properly.
    vector_store=vector_store,
    validate_arguments=False,
)

loadpath = "./pipeline_storage"
if os.path.exists(loadpath):
    pipeline.load(persist_dir=loadpath)
# run the pipeline
nodes = pipeline.run(documents=[Document.example()])  # return newly added nodes.
import rich

# rich.print(nodes)
# rich.print(pipeline.documents)
# rich.print(pipeline.docstore.docs)
pipeline.persist(persist_dir=loadpath)  # not persisting document.
serv_cont = ServiceContext.from_defaults(
    llm_predictor=LLMPredictor(llm),
    embed_model=embed,
)

# vsindex = VectorStoreIndex.from_vector_store(vectore_store)
vsindex = VectorStoreIndex.from_vector_store(vector_store, service_context=serv_cont)
# vsindex = VectorStoreIndex.from_documents(pipeline.docstore.docs.values(),service_context=serv_cont)

# this will do RAG. However do you have qualified prompt?
# engine = vsindex.as_query_engine()

engine = vsindex.as_retriever()
ans = engine.retrieve("hello")
# ans = engine.query("something interesting in the document")
rich.print(ans)
