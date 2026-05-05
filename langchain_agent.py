import os, json
import time
from dotenv import load_dotenv
from typing import TypedDict, List


from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=os.getenv("GROQ_API_KEY"))
load_dotenv()


class AgentState(TypedDict):
    goal: str
    tasks: List[str]
    results: List[str]
    critique: str
    approved: bool
    iterations: int

Search = DuckDuckGoSearchRun()


def planner(state: AgentState) -> AgentState: 
    system = """You are a planning agent. Break the user's goal into at most 3 concrete, actionable tasks. Respond ONLY with a valid JSON array of strings. No preamble, no markdown."""

    messages = [
        SystemMessage(content=system), 
        HumanMessage(content=f"Goal: {state['goal']}")
    ]
    response = llm.invoke(messages).content.strip()

    try:
        clean = response.replace("```json", "").replace("```", "").strip()
        tasks = json.loads(clean) 
    except json. JSONDecodeError:
        tasks = [response] # fallback: treat whole response as one task

    print(f"\n[Planner] Generated {len(tasks)} tasks:") 
    for i, t in enumerate(tasks): print(f" {i+1}. {t}")

    return {**state, "tasks": tasks}

def executor(state: AgentState) -> AgentState:
    results = []
    critique_ctx = ""

    if state["critique"]:
        critique_ctx = f"\n\nYour previous attempt was rejected. Critique: {state['critique']}\nImprove your output accordingly."

    for task in state["tasks"]:
        system = f"""You are an execution agent. Complete the task below thoroughly.
        Use web search if you need current information.{critique_ctx}"""

        # try web search for research tasks
        search_ctx = ""
        try:
            search_result = Search.run(task[:100])
            search_ctx = f"\n\nWeb search result for context:\n{search_result[:300]}"
        except:
            pass

        messages = [
            SystemMessage(content=system),
            HumanMessage(content=f"Task: {task}{search_ctx}")
        ]

        def safe_llm_call(messages):
            for _ in range(3):  # retry 3 times
                try:
                    return llm.invoke(messages).content
                except Exception as e:
                    if "Rate limit" in str(e) or "429" in str(e):
                        time.sleep(1)  # wait 1 sec
                    else:
                        raise e
            return "Error: Rate limit"
        result = safe_llm_call(messages)
        results.append(result)
        print(f"\n[Executor] Task: {task[:60]}...\n Result: {result[:120]}...")

    return {
        **state,
        "results": results,
        "iterations": state["iterations"] + 1
    }

def verifier(state: AgentState) -> AgentState:
    # safety net — approve after 3 iterations regardless
    if state["iterations"] >= 2:
        print("[Verifier] Max iterations reached — force approving.")
        return {**state, "approved": True}

    combined_results = "\n\n".join(
        f"Task {i+1}: {t}\nResult: {r}"
        for i, (t, r) in enumerate(zip(state["tasks"], state["results"]))
    )

    system = """You are a quality verifier. Evaluate the results against the original goal using this rubric:
- Completeness: Does it fully address the goal? (0–0.4)
- Accuracy: Is the information correct and specific? (0–0.3)
- Clarity: Is it well-structured and clear? (0–0.3)

Sum the scores for a total between 0.0 and 1.0.
Respond ONLY as JSON: {"score": 0.85, "approved": true, "critique": "..."}"""

    messages = [
        SystemMessage(content=system),
        HumanMessage(content=f"Original goal: {state['goal']}\n\nResults:\n{combined_results}")
    ]

    raw = llm.invoke(messages).content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        verdict = json.loads(clean)

        approved = verdict.get("approved", False)
        critique = verdict.get("critique", "")
        score = verdict.get("score", 0)

    except:
        approved, critique, score = False, raw, 0

    print(f"\n[Verifier] Score: {score:.2f} | Approved: {approved}")

    return {
        **state,
        "approved": approved,
        "critique": critique
    }
########################################
graph = StateGraph(AgentState)

graph.add_node("planner", planner)
graph.add_node("executor", executor)
graph.add_node("verifier", verifier)

graph.set_entry_point("planner")

graph.add_edge("planner", "executor")
graph.add_edge("executor", "verifier")

# 🔥 CONDITIONAL LOOP
def route_verifier(state: AgentState):
    if state["approved"]:
        return END
    else:
        return "executor"

graph.add_conditional_edges("verifier", route_verifier)

app = graph.compile()

# ================= RUN =================
initial_state = AgentState(
    goal="Research and summarize the top 3 trends in generative AI for 2025.",
    tasks=[],
    results=[],
    critique="",
    approved=False,
    iterations=0
)

final_state = app.invoke(initial_state)

print("\n======FINAL OUTPUT======")

for i, (task, result) in enumerate(zip(final_state["tasks"], final_state["results"])):
    print(f"\n[Task {i+1}]: {task}\nResult: {result}")

print(f"\nCompleted in {final_state['iterations']} iteration(s).")
# -------------------------
# Example usage (test run)
# -------------------------
'''
if __name__ == "__main__":
    query = "Latest news about AI"

    result = search.run(query)
    print("\n🔍 Search Result:\n", result)

    response = llm.invoke([
        HumanMessage(content=f"Summarize this:\n{result}")
    ])

    print("\n🤖 LLM Response:\n", response.content)
    '''