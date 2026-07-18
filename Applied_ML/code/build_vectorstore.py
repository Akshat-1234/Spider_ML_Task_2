import json
import pandas as pd
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


#Project directories

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DATA_DIR = PROJECT_DIR/"data"
VECTORSTORE_DIR = PROJECT_DIR/"vectorstore"


documents = []
guideline_documents = []


#Loading MedQuAD

print("Loading MedQuAD...")

df = pd.read_csv(DATA_DIR/"medquad.csv")

for index,row in df.iterrows():

    question = str(row["question"]).strip()
    answer = str(row["answer"]).strip()

    text = f"""Question:
{question}

Answer:
{answer}
"""

    documents.append(
        Document(
            page_content=text,
            metadata={
                "id":index,
                "type":"qa",
                "source":"MedQuAD",
                "question":question,
                "answer":answer
            }
        )
    )


#Loading WHO Documents

print("Loading WHO Documents...")

WHO_DIR = DATA_DIR/"WHO"

for file in WHO_DIR.glob("*.json"):

    with open(file,"r",encoding="utf-8") as f:
        data = json.load(f)

    guideline_documents.append(
        Document(
            page_content=data["text"],
            metadata={
                "type":"guideline",
                "source":data["source"],
                "title":data["title"],
                "url":data["url"]
            }
        )
    )


#Loading CDC Documents (Optional)

CDC_DIR = DATA_DIR/"CDC"

if CDC_DIR.exists():

    print("Loading CDC Documents...")

    for file in CDC_DIR.glob("*.json"):

        with open(file,"r",encoding="utf-8") as f:
            data = json.load(f)

        guideline_documents.append(
            Document(
                page_content=data["text"],
                metadata={
                    "type":"guideline",
                    "source":data["source"],
                    "title":data["title"],
                    "url":data["url"]
                }
            )
        )


#Loading NICE Documents (Optional)

NICE_DIR = DATA_DIR/"NICE"

if NICE_DIR.exists():

    print("Loading NICE Documents...")

    for file in NICE_DIR.glob("*.json"):

        with open(file,"r",encoding="utf-8") as f:
            data = json.load(f)

        guideline_documents.append(
            Document(
                page_content=data["text"],
                metadata={
                    "type":"guideline",
                    "source":data["source"],
                    "title":data["title"],
                    "url":data["url"]
                }
            )
        )


#Splitting guideline documents

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

guideline_chunks = splitter.split_documents(
    guideline_documents
)

documents.extend(guideline_chunks)

print(f"Created {len(documents)} Documents")


#Loading embedding model

embeddings = HuggingFaceEmbeddings(
    model_name="NeuML/pubmedbert-base-embeddings"
)


#Building the vectorstore

vectorstore = FAISS.from_documents(
    documents,
    embeddings
)


#Saving the vectorstore

VECTORSTORE_DIR.mkdir(exist_ok=True)

vectorstore.save_local(
    str(VECTORSTORE_DIR)
)


#Verifying the vectorstore

results = vectorstore.similarity_search(
    "What are the symptoms of hypertension?",
    k=3
)

for doc in results:

    print("\nSOURCE:",doc.metadata["source"])

    if doc.metadata["type"] == "qa":
        print("QUESTION:",doc.metadata["question"])

    else:
        print("TITLE:",doc.metadata["title"])

    print(doc.page_content[:300])

print("\nVector Store Created Successfully!")
