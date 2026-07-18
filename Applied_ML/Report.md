# Healthcare Information Assistant using RAG

This project was developed as part of **SPIDER ML Task 2**. The objective was to build a Retrieval-Augmented Generation (RAG) based healthcare assistant that answers medical questions using trusted medical sources instead of relying only on a language model's internal knowledge.

The assistant retrieves relevant information from a medical knowledge base, reranks the retrieved documents, checks for unsafe queries, verifies the generated answer against the retrieved evidence, and estimates a confidence score, using a locally running Llama 3 model.

## Features

- Retrieval-Augmented Generation (RAG)
- Medical question answering
- Uses MedQuAD dataset and WHO Fact Sheets
- FAISS vector database for semantic search using a biomedical embedding model
- CrossEncoder reranking for improved retrieval
- Confidence estimation for generated responses
- Faithfulness check to catch answers not backed by the retrieved context
- Safety checks for diagnosis, prescriptions, emergencies, and self harm
- Streamlit web interface
- Runs completely locally using Ollama

## Project Structure

```
SPIDER_ML_TASK_2/
│
├── Applied_ML/
│   ├── code/
│   │   ├── app.py
│   │   ├── rag.py
│   │   ├── build_vectorstore.py
│   │   ├── scraper.py
│   │   ├── safety.py
│   │   ├── confidence.py
│   │   ├── faithfulness.py
│   │   └── eval.py
│   │
│   ├── data/
│   │   ├── medquad.csv
│   │   └── WHO/
│   │
│   └── vectorstore/
│
└── requirements.txt
```

## Dataset

### MedQuAD

MedQuAD is a medical Question-Answer dataset released by the U.S. National Library of Medicine. It contains thousands of healthcare-related questions and answers covering diseases, symptoms, treatments, genetics, and medical conditions.

### WHO Fact Sheets

WHO fact sheets are scraped from the official World Health Organization website. Each article is stored as a JSON file containing:

- Title
- Source
- URL
- Full article text

Long WHO articles are split into smaller chunks before indexing. The scraper now retries failed requests and waits between pages so it doesn't get blocked.

## Workflow

```
User Question
      │
      ▼
Safety Check
      │
      ▼
FAISS Retrieval (biomedical embeddings)
      │
      ▼
CrossEncoder Reranking
      │
      ▼
Confidence Estimation
      │
      ▼
Llama 3 (Ollama)
      │
      ▼
Faithfulness Check
      │
      ▼
Generated Response
```

## Technologies Used

- Python
- Streamlit
- FAISS
- LangChain
- HuggingFace Embeddings (PubMedBERT)
- Sentence Transformers
- CrossEncoder
- Ollama
- Llama 3
- BeautifulSoup

## Installation

Clone the repository.

```bash
git clone <repository-url>
cd SPIDER_ML_TASK_2
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

Windows

```bash
.venv\Scripts\activate
```

Linux / Mac

```bash
source .venv/bin/activate
```

Install the dependencies.

```bash
pip install -r requirements.txt
```

## Download Llama 3

Install Ollama and download the model.

```bash
ollama pull llama3
```

Start Ollama before running the application.

```bash
ollama serve
```

## Building the Vector Database

After placing the datasets inside the `data` folder, create the FAISS vector database.

```bash
python -m Applied_ML.code.build_vectorstore
```

Note: if you already had a vectorstore built with the old MiniLM embeddings, you need to rebuild it, since `rag.py` now loads queries with a different (biomedical) embedding model and the dimensions won't match otherwise.

## Running the Application

Launch the Streamlit application.

```bash
streamlit run Applied_ML/code/app.py
```

## Running the Evaluation

A small evaluation script is included to sanity check retrieval and answer quality on a handful of labeled questions.

```bash
python -m Applied_ML.code.eval
```

It reports, out of the test questions: how many returned at least one retrieved document, and how many answers contained at least one expected keyword. It's not a rigorous benchmark, just a quick way to catch regressions instead of manually testing questions by hand every time something changes.

## Example Questions

- What are the symptoms of hypertension?
- What causes diabetes?
- What are the risk factors for stroke?
- How can asthma be managed?
- What is dengue fever?

## Safety Features

The assistant does not provide:

- Medical diagnosis
- Prescription recommendations
- Medication dosage
- Emergency medical advice

Self harm / suicide related messages are also caught separately and routed to a supportive message encouraging the user to reach out to a crisis line or someone they trust, instead of being treated the same as a general emergency.

For such questions, the system advises the user to consult a qualified healthcare professional or emergency services.

## Confidence Scoring

The confidence score is based on the CrossEncoder reranker scores. Since the reranker actually outputs raw logits and not a 0-1 probability, the scores are now passed through a sigmoid before being averaged, so the resulting number is at least mathematically meaningful. It is still a hand tuned heuristic and not calibrated against real correctness labels, so it should be read as a rough indicator rather than an exact probability.

## Faithfulness Check

After Llama 3 generates an answer, a second LLM call checks whether the answer's claims are actually supported by the retrieved context. If the check fails, a warning is appended to the answer so the user knows to double check it. This adds one extra LLM call per question but helps catch hallucinations before they reach the user, which matters a lot more in a healthcare context than in a general chatbot.

## Limitations

- Responses depend on the available indexed documents.
- Confidence score is only an estimate, not a calibrated probability.
- The faithfulness check is itself an LLM call and can occasionally be wrong (it's not a perfect hallucination detector).
- The assistant is not a replacement for professional medical advice.
- WHO documents need to be updated periodically by running the scraper again.
- The evaluation set in `eval.py` is small and handmade, a larger labeled set would give more reliable numbers.

## Future Improvements

- Add CDC and NICE medical guidelines.
- Hybrid retrieval using BM25 and embeddings.
- Better citation support.
- Medical entity recognition.
- Automatic updating of medical documents.
- Expand the evaluation set and compare retrieval metrics (recall@k) between the old MiniLM embeddings and the new biomedical embeddings.
- Replace the keyword based safety check with a lightweight classifier for better recall on paraphrased emergency/self harm queries.

## Acknowledgements

- MedQuAD Dataset
- World Health Organization (WHO)
- LangChain
- HuggingFace
- Ollama
- Streamlit