# =========================
# router_chatbot_with_eval.py
# =========================

import os
import time
from dotenv import load_dotenv
from typing import TypedDict

from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq


# =========================
# Load Environment
# =========================
load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)


# =========================
# State Definition
# =========================
class AgentState(TypedDict):
    query: str
    context: str
    answer: str
    latency: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    completeness_score: float


# =========================
# Router Node
# =========================
def router(state: AgentState) -> AgentState:
    return state


# =========================
# Routing Logic
# =========================
def route_query(state: AgentState):
    query = state["query"].lower()

    if any(op in query for op in ["+", "-", "*", "/", "calculate"]):
        print("\n🔀 Routed to: MATH")
        return "math"

    elif any(word in query for word in ["explain", "notes", "week", "attention", "define"]):
        print("\n🔀 Routed to: RETRIEVER")
        return "retriever"

    else:
        print("\n🔀 Routed to: DIRECT LLM")
        return "direct"


# =========================
# Direct LLM Node
# =========================
def direct_llm(state: AgentState) -> AgentState:
    print("➡️ Executing: DIRECT LLM")

    query = state["query"]

    start = time.time()
    response = llm.invoke(query)
    end = time.time()

    usage = response.response_metadata.get("token_usage", {})

    return {
        **state,
        "context": "",
        "answer": response.content,
        "latency": end - start,
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0)
    }


# =========================
# Retriever Node (Mock)
# =========================
def retriever(state: AgentState) -> AgentState:
    print("➡️ Executing: RETRIEVER")

    query = state["query"]

    # Mock context (replace later with real RAG)
    context = f"Relevant information about: {query}"

    return {
        **state,
        "context": context
    }


# =========================
# Math Node
# =========================
def math_node(state: AgentState) -> AgentState:
    print("➡️ Executing: MATH NODE")

    query = state["query"]

    try:
        result = str(eval(query))
    except:
        result = "Invalid math expression"

    return {
        **state,
        "context": "",
        "answer": result,
        "latency": 0.0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }


# =========================
# Generator Node
# =========================
def generator(state: AgentState) -> AgentState:
    print("➡️ Generating final answer...")

    query = state["query"]
    context = state.get("context", "")

    prompt = f"""
    Answer the question clearly.

    Context:
    {context}

    Question:
    {query}
    """

    start = time.time()
    response = llm.invoke(prompt)
    end = time.time()

    usage = response.response_metadata.get("token_usage", {})

    return {
        **state,
        "answer": response.content,
        "latency": end - start,
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0)
    }


# =========================
# Evaluator Node (Completeness)
# =========================
def evaluator(state: AgentState) -> AgentState:
    print("➡️ Evaluating answer...")

    query = state["query"]
    answer = state["answer"]

    prompt = f"""
    Evaluate the answer based on COMPLETENESS only.

    Question: {query}
    Answer: {answer}

    Give score between 0 and 1.
    ONLY return number (example: 0.85)
    """

    response = llm.invoke(prompt).content.strip()

    try:
        score = float(response)
    except:
        score = 0.0

    return {
        **state,
        "completeness_score": score
    }


# =========================
# Build Graph
# =========================
graph = StateGraph(AgentState)

graph.add_node("router", router)
graph.add_node("direct", direct_llm)
graph.add_node("retriever", retriever)
graph.add_node("math", math_node)
graph.add_node("generator", generator)
graph.add_node("evaluator", evaluator)

graph.set_entry_point("router")

# Routing
graph.add_conditional_edges("router", route_query)

# Merge paths
graph.add_edge("direct", "generator")
graph.add_edge("retriever", "generator")
graph.add_edge("math", "generator")

# Evaluation
graph.add_edge("generator", "evaluator")
graph.add_edge("evaluator", END)

app = graph.compile()


# =========================
# Run
# =========================
if __name__ == "__main__":

    while True:
        user_query = input("\n💬 Ask something (or type 'exit'): ")

        if user_query.lower() == "exit":
            break

        initial_state = {
            "query": user_query,
            "context": "",
            "answer": "",
            "latency": 0.0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "completeness_score": 0.0
        }

        result = app.invoke(initial_state)

        print("\n🤖 Answer:")
        print(result["answer"])

        print("\n📊 Metrics:")
        print(f"Latency: {result['latency']:.2f}s")
        print(f"Tokens: {result['total_tokens']} (Input: {result['input_tokens']}, Output: {result['output_tokens']})")
        print(f"Completeness Score: {result['completeness_score']}")