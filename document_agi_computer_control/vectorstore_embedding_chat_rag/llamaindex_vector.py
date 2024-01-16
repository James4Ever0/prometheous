from llama_index import VectorStoreIndex, LLMPredictor
from llama_index import Document
from llama_index.llms import Ollama
from llama_index.embeddings import OllamaEmbedding
from llama_index import ServiceContext

embed = OllamaEmbedding(model_name="openhermes2.5-mistral:latest")
llm = Ollama(model="openhermes2.5-mistral:latest")
serv_cont = ServiceContext.from_defaults(
    llm_predictor=LLMPredictor(llm),
    embed_model=embed,
)

documents = [Document.example()]
# print(documents)
index = VectorStoreIndex.from_documents(documents, service_context=serv_cont)
