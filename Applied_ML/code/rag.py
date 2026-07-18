import time
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from sentence_transformers import CrossEncoder

import sys

sys.path.append(str(Path(__file__).parent))

from confidence import calculate_confidence
from safety import safety_check
from faithfulness import check_faithfulness

#Loading embedding model

embeddings = HuggingFaceEmbeddings(
    model_name="NeuML/pubmedbert-base-embeddings"
)


#Loading vectorstore

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

vectorstore = FAISS.load_local(
    str(PROJECT_DIR/"vectorstore"),
    embeddings,
    allow_dangerous_deserialization=True
)


#Loading Llama

llm = ChatOllama(
    model="llama3:latest",
    temperature=0.2,
    num_ctx=8192
)


#Loading reranker

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


def rerank_results(question,results,top_k=8):

    pairs = []

    for doc,score in results:
        pairs.append((question,doc.page_content))

    scores = reranker.predict(pairs)

    ranked = list(zip(results,scores))

    ranked.sort(
        key=lambda x:x[1],
        reverse=True
    )

    results = []
    rerank_scores = []

    for item,score in ranked[:top_k]:
        results.append(item)
        rerank_scores.append(float(score))

    return results,rerank_scores


def answer_question(question):

    safe,message = safety_check(question)

    if not safe:
        return message,"N/A",0,[],[],True


    #Retrieving documents

    start = time.time()

    results = vectorstore.similarity_search_with_score(
        question,
        k=15
    )

    print("Retrieval:",time.time()-start)


    #Reranking

    results,scores = rerank_results(
        question,
        results
    )


    context = ""
    docs = []
    sources = []
    seen = set()

    for doc,score in results:

        docs.append(doc)

        if doc.metadata["type"]=="qa":

            context += f"""
Source: {doc.metadata["source"]}

Question:
{doc.metadata["question"]}

Answer:
{doc.metadata["answer"]}

"""

            key = (
                doc.metadata["source"],
                doc.metadata["question"]
            )

            if key not in seen:
                sources.append({
                    "source":doc.metadata["source"],
                    "question":doc.metadata["question"]
                })
                seen.add(key)

        else:

            context += f"""
Source: {doc.metadata["source"]}

Title:
{doc.metadata["title"]}

Content:
{doc.page_content}

"""

            key = (
                doc.metadata["source"],
                doc.metadata["title"]
            )

            if key not in seen:
                sources.append({
                    "source":doc.metadata["source"],
                    "title":doc.metadata["title"],
                    "url":doc.metadata["url"]
                })
                seen.add(key)


    confidence_level,confidence_score = calculate_confidence(
        scores,
        sources
    )


    prompt = f"""
You are a trustworthy Healthcare Information Assistant.

Use ONLY the provided evidence.

If evidence is insufficient, say so clearly.

Do not diagnose diseases.
Do not prescribe medicines or dosages.

Answer:

{context}

Question:
{question}
"""


    start = time.time()

    try:
        response = llm.invoke(prompt)

    except Exception as e:
        return str(e),confidence_level,confidence_score,sources,docs,True

    print("Generation:",time.time()-start)

    answer = response.content

    #Checking faithfulness

    faithful = check_faithfulness(llm,question,context,answer)

    if not faithful:
        answer += "\n\n*Note: parts of this answer could not be fully verified against the retrieved sources. Please double check with a healthcare professional.*"

    return (
        answer,
        confidence_level,
        confidence_score,
        sources,
        docs,
        faithful
    )


if __name__=="__main__":

    answer,level,score,sources,docs,faithful = answer_question(
        "What are the symptoms of hypertension?"
    )

    print("\nAnswer\n")
    print(answer)

    print("\nConfidence:",level,score)

    print("\nFaithful:",faithful)

    print("\nSources")

    for source in sources:
        print(source)
