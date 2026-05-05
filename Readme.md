## Intent-Based AI Chatbot with Routing + Evaluation Metrics

---

## 📌 Overview

This project implements a **smart chatbot system** that dynamically routes user queries to different processing pipelines based on intent.

Unlike a simple LLM chatbot, this system:

* Routes queries intelligently (Math / Knowledge / General)
* Uses LLM + optional retrieval
* Evaluates responses using metrics:

  * **Latency**
  * **Token usage**
  * **Completeness score**

---

## 🧠 System Architecture

```text
User Query
   ↓
Intent Router
   ↓
 ┌───────────────┬───────────────┬───────────────┐
 ↓               ↓               ↓
Math           Retriever        Direct LLM
 ↓               ↓               ↓
       └──────→ Generator ←──────┘
                      ↓
                 Evaluator
                      ↓
                Final Answer
```

---

## ⚙️ Components

### 1️⃣ Intent Router

* Classifies user query into:

  * Math
  * Retriever (RAG-style)
  * Direct LLM

---

### 2️⃣ Math Node

* Uses Python `eval()` for calculations

---

### 3️⃣ Retriever Node (Mock)

* Placeholder for RAG (can be replaced with FAISS/BM25)

---

### 4️⃣ Direct LLM Node

* Sends query directly to LLM

---

### 5️⃣ Generator Node

* Combines context + query → final answer

---

### 6️⃣ Evaluator Node

Evaluates answer based on:

| Metric       | Description                    |
| ------------ | ------------------------------ |
| Latency      | Response time                  |
| Tokens       | Input + Output tokens          |
| Completeness | Coverage of answer (0–1 score) |

---

## 🧩 Tech Stack

| Component | Technology       |
| --------- | ---------------- |
| LLM       | Groq (LLaMA 3.1) |
| Framework | LangGraph        |
| Language  | Python           |
| Env       | python-dotenv    |

---

## 📂 Project Structure

```text
multiagent/
│
|── langchain_agent.py
├── router_chatbot.py
├── .env
├── .gitignore
└── README.md
```

---

## ⚡ How to Run

### 1️⃣ Activate Environment

```bash
venv\Scripts\activate
```

---

### 2️⃣ Install Dependencies

```bash
pip install langchain langgraph langchain-groq python-dotenv
```

---

### 3️⃣ Add API Key

Create `.env`:

```env
GROQ_API_KEY=your_api_key_here
```

---

### 4️⃣ Run

```bash
python router_chatbot.py
```

---

## 🧪 Sample Outputs

---

### 🔹 Example 1: Math Query

```text
💬 Ask something: what is 2+2

🔀 Routed to: MATH
➡️ Executing: MATH NODE
➡️ Generating final answer...
➡️ Evaluating answer...

🤖 Answer:
The answer to 2+2 is 4.

📊 Metrics:
Latency: 0.28s
Tokens: 69 (Input: 57, Output: 12)
Completeness Score: 0.8
```

---

### 🔹 Example 2: General Knowledge

```text
💬 Ask something: who is prime minister of india

🔀 Routed to: DIRECT LLM
➡️ Executing: DIRECT LLM
➡️ Generating final answer...
➡️ Evaluating answer...

🤖 Answer:
The current Prime Minister of India is Narendra Modi...

📊 Metrics:
Latency: 0.19s
Tokens: 87 (Input: 57, Output: 30)
Completeness Score: 0.85
```

---

### 🔹 Example 3: Conceptual Query (Retriever Path)

```text
💬 Ask something: what is self attention

🔀 Routed to: RETRIEVER
➡️ Executing: RETRIEVER
➡️ Generating final answer...
➡️ Evaluating answer...

🤖 Answer:
Self-attention is a fundamental concept in deep learning...

📊 Metrics:
Latency: 1.12s
Tokens: 682 (Input: 64, Output: 618)
Completeness Score: 0.98
```

---

## 📊 Metrics Explained

### 🔹 Tokens

* Units of text processed by LLM
* Directly impact cost

---

### 🔹 Latency

* Time taken to generate response
* Indicates performance

---

### 🔹 Completeness Score

* LLM-evaluated quality of answer
* Range: `0 → 1`

---

## 🧠 Key Features

✔ Intent-based routing
✔ Multi-path execution
✔ LLM-powered answers
✔ Evaluation metrics
✔ Modular architecture

---

## ⚠️ Limitations

* Retriever is currently mock (not real RAG)
* No memory across queries
* Completeness ≠ factual accuracy
* Uses `eval()` (unsafe for production math)

---

## 🚀 Future Improvements

* Replace retriever with FAISS / BM25
* Add conversation memory
* Add accuracy / hallucination detection
* Build FastAPI backend
* Add React UI

---

## 💡 Key Learning

```text
LLM alone is not enough.
Routing + Evaluation = Smarter AI System
```

---

## 👨‍💻 Author

**Himkar Vashistha**
AI / Data Science Engineer

---

## ⭐ Final Note

This project demonstrates a **foundation of agentic AI systems** used in:

* RAG pipelines
* Intelligent assistants
* Multi-tool LLM systems



