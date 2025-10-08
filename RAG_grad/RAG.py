import os
from langchain_openai import ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
from ingestion.build_vectorstore import build_db
from prompt_template import prompt_template
from dotenv import load_dotenv
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers import ContextualCompressionRetriever

load_dotenv()
API_KEY = os.getenv("API_KEY")

embedding_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")


llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    base_url="https://api.groq.com/openai/v1",
    api_key=API_KEY
)

vectorDB=build_db()

def get_answer(query: str, major: str = None):
    
    retriever = vectorDB.as_retriever(
        search_kwargs={"k": 7, "filter": {"major": major}}
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

    result = qa_chain.invoke(query)

    answer = {
        "result": result["result"],
        "sources": [doc.metadata.get("name", "غير معروف") for doc in result["source_documents"]]
    }
    return answer