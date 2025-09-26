from langchain_huggingface import HuggingFaceEmbeddings   # ✅ التعديل هنا
from langchain_chroma import Chroma
from loaders import all_docs

embedding_model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
def build_db():
    vectorDB = Chroma(
        collection_name="my_docs",
        embedding_function=embedding_model,
        persist_directory="./chroma/db"
    )
    existing = vectorDB.get()
    if existing and len(existing["ids"]) > 0:
        print("DB already exists, skipping adding docs.")
    else:
        vectorDB.add_documents(all_docs)
        print("Docs added and DB persisted.")
    return vectorDB

build_db()
print("done")
