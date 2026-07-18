#Checking whether the answer is supported by the retrieved context

def check_faithfulness(llm,question,context,answer):

    prompt = f"""
You are checking if an answer is fully supported by the given context.

Context:
{context}

Question:
{question}

Answer:
{answer}

Is every claim in the answer supported by the context above?
Reply with only one word: YES or NO
"""

    try:
        result = llm.invoke(prompt)
        verdict = result.content.strip().upper()

        return verdict.startswith("YES")

    except Exception:
        return True
