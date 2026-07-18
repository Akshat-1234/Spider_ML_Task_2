#Quick evaluation on a small labeled test set

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from rag import answer_question

test_set = [
    {
        "question":"What are the symptoms of hypertension?",
        "expected_keywords":["headache","dizziness","blood pressure"]
    },
    {
        "question":"What causes diabetes?",
        "expected_keywords":["insulin","blood sugar","glucose"]
    },
    {
        "question":"What is dengue fever?",
        "expected_keywords":["mosquito","fever","virus"]
    },
    {
        "question":"How can asthma be managed?",
        "expected_keywords":["inhaler","airway","trigger"]
    },
    {
        "question":"What are the risk factors for stroke?",
        "expected_keywords":["blood pressure","smoking","cholesterol"]
    },
    {
        "question":"I think I am having a heart attack, what should I do?",
        "expected_keywords":["emergency"]
    }
]


def run_eval():

    total = len(test_set)
    keyword_hits = 0
    retrieved_something = 0

    for case in test_set:

        answer,level,score,sources,docs,faithful = answer_question(case["question"])

        print("\nQ:",case["question"])
        print("Confidence:",level,score)
        print("Faithful:",faithful)

        if len(docs) > 0:
            retrieved_something += 1

        answer_lower = answer.lower()

        hit = False

        for keyword in case["expected_keywords"]:
            if keyword in answer_lower:
                hit = True
                break

        if hit:
            keyword_hits += 1
            print("Result: PASS")
        else:
            print("Result: FAIL")

    print("\n----- Summary -----")
    print(f"Retrieved at least 1 doc: {retrieved_something}/{total}")
    print(f"Answer keyword match: {keyword_hits}/{total}")


if __name__=="__main__":
    run_eval()