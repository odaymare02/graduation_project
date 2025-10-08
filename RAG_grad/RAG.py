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

# def get_answer(query: str, major: str = None):
    
#     retriever = vectorDB.as_retriever(
#         search_kwargs={"k": 7, "filter": {"major": major}}
#     )

#     qa_chain = RetrievalQA.from_chain_type(
#         llm=llm,
#         retriever=retriever,
#         return_source_documents=True,
#         chain_type_kwargs={"prompt": prompt_template}
#     )

#     result = qa_chain.invoke(query)

#     answer = {
#         "result": result["result"],
#         "sources": [doc.metadata.get("name", "غير معروف") for doc in result["source_documents"]]
#     }
#     return answer
from datetime import datetime

def get_answer(query: str, major: str = None):
       # 1️⃣ إعداد retriever من قاعدة البيانات
    retriever = vectorDB.as_retriever(
        search_kwargs={"k": 10, "filter": {"major": major} if major else None}
    )

    # 2️⃣ جلب النتائج الأولية قبل rerank
    initial_docs = retriever.get_relevant_documents(query)

    # 3️⃣ إنشاء prompt المرحلة الأولية قبل rerank
    initial_prompt = prompt_template.format(
        question=query,
        context="\n\n".join([doc.page_content for doc in initial_docs])
    )

    # حفظ prompt المرحلة الأولية مع timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    initial_file = f"prompt_before_rerank_{timestamp}.txt"
    with open(initial_file, "w", encoding="utf-8") as f:
        f.write(initial_prompt)

    # 4️⃣ إعداد reranker
    # reranker = LLMChainFilter.from_llm(llm)
    # rerank_retriever = ContextualCompressionRetriever(
    #     base_compressor=reranker,
    #     base_retriever=retriever
    # )

    # 5️⃣ جلب الوثائق بعد rerank
    # reranked_docs = rerank_retriever.get_relevant_documents(query)

    # 6️⃣ إنشاء prompt بعد rerank
    # rerank_prompt = prompt_template.format(
    #     question=query,
    #     context="\n\n".join([doc.page_content for doc in reranked_docs])
    # )

    # حفظ prompt بعد rerank
    # rerank_file = f"prompt_after_rerank_{timestamp}.txt"
    # with open(rerank_file, "w", encoding="utf-8") as f:
    #     f.write(rerank_prompt)

    # 7️⃣ إنشاء QA chain مع retriever بعد rerank
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt_template}
    )

    # 8️⃣ استدعاء الإجابة النهائية
    result = qa_chain.invoke(query)

    answer = {
        "result": result["result"],
        "sources": [doc.metadata.get("name", "غير معروف") for doc in result["source_documents"]]
    }
    return answer