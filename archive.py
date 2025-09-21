from dotenv import load_dotenv
from typing import Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

load_dotenv()

# Initialize the Groq LLM
llm = init_chat_model(
    model="gemma2-9b-it", model_provider="groq"
)

# --- Structured output model to decide next agent ---
class NextAgentClassifier(BaseModel):
    next_agent: str = Field(
        ...,
        description="Decide which agent should handle the next message: 'therapist' or 'logical'."
    )

# --- State structure ---
class State(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str | None

# --- Agents ---
def therapist_agent(state: State):
    last_message = state["messages"][-1]
    messages = [
        {"role": "system",
         "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                        Show empathy, validate feelings, and help process emotions.
                        Ask thoughtful questions. Avoid giving logical solutions unless explicitly asked."""},
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def logical_agent(state: State):
    last_message = state["messages"][-1]
    messages = [
        {"role": "system",
         "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Avoid addressing emotions. Be direct and straightforward."""},
        {"role": "user", "content": last_message.content}
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

# --- LLM-based router ---
def router(state: State):
    last_message = state["messages"][-1]
    classifier_llm = llm.with_structured_output(NextAgentClassifier)

    result = classifier_llm.invoke([
        {"role": "system",
         "content": """Read the user message and decide which agent should respond next:
                      - 'therapist': if the message needs emotional support, feelings, therapy, or empathy
                      - 'logical': if the message needs facts, calculations, logical reasoning, or practical help
                      Respond only with the agent name in JSON format as {"next_agent": "<agent_name>"}."""},
        {"role": "user", "content": last_message.content}
    ])

    return {"next_agent": result.next_agent.lower()}

# --- Graph setup ---
graph_builder = StateGraph(State)

graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)

graph_builder.add_edge(START, "router")

graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next_agent"),
    {"therapist": "therapist", "logical": "logical"}
)

graph_builder.add_edge("therapist", END)
graph_builder.add_edge("logical", END)

graph = graph_builder.compile()

# --- Run chatbot ---
def run_chatbot():
    state = {"messages": [], "next_agent": None}

    print("Type 'exit' to quit.")
    while True:
        user_input = input("Message: ")
        if user_input.lower() == "exit":
            print("Bye")
            break

        state["messages"] = state.get("messages", []) + [{"role": "user", "content": user_input}]
        state = graph.invoke(state)

        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"{last_message.role.capitalize()} Agent: {last_message.content}")

if __name__ == "__main__":
    run_chatbot()
