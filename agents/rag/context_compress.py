# Helper function for printing docs

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
OPENAI_API_KEY = "sk-2cmthChvoTpVLsZzAe5bE435A67741FcB220E8788dA367A3"
OPENAI_BASE_URL = "https://one.aios123.com/v1/"
documents = TextLoader("/Users/cqs/Documents/研究生学习/代码/LLM-Medical-Agent/data/1103749.json").load()
def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(documents)
retriever = FAISS.from_documents(texts, OpenAIEmbeddings(openai_api_key = "sk-2cmthChvoTpVLsZzAe5bE435A67741FcB220E8788dA367A3",openai_api_base = "https://one.aios123.com/v1/")).as_retriever()

docs = retriever.invoke("What did the president say about Ketanji Brown Jackson")
# pretty_print_docs(docs)

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import OpenAI

llm = OpenAI( model="gpt4o-mini",temperature=0,openai_api_key = "sk-2cmthChvoTpVLsZzAe5bE435A67741FcB220E8788dA367A3",openai_api_base = "https://one.aios123.com/v1/")
compressor = LLMChainExtractor.from_llm(llm)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor, base_retriever=retriever
)

compressed_docs = compression_retriever.invoke(
    "What did the president say about Ketanji Jackson Brown"
)
pretty_print_docs(compressed_docs)