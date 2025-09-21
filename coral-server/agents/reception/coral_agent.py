from dotenv import load_dotenv
from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
import os
from openai import OpenAI
from langchain.chat_models import init_chat_model

load_dotenv()

# ---- OpenAI client for routing ----
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai_client = OpenAI(
#     base_url="https://api.aimlapi.com/v1",
#     api_key=OPENAI_API_KEY
# )

# ---- Initialize Groq LLM for responses ----


llm = init_chat_model(
    model="gemma2-9b-it", model_provider="groq"
)

# ---- Structured Output for Classification (optional, kept for logging) ----
class MessageClassifier(BaseModel):
    message_type: Literal["emotional", "logical"] = Field(
        ..., description="Classify if the message requires an emotional or logical response."
    )

# ---- State Definition ----
class State(TypedDict):
    messages: Annotated[list, add_messages]
    message_type: str | None

# ---- Base Agent ----
class BaseAgent:
    def __init__(self, name: str):
        self.name = name
        self.state: State = {"messages": [], "message_type": None}

    def add_message(self, role: str, content: str):
        self.state["messages"].append({"role": role, "content": content})

    def respond(self):
        """Override in subclasses"""
        return {"messages": []}

    def decide_next_agent(self, agents: dict):
        """Use OpenAI to route the next agent based on the latest user message"""
        last_message = self.state["messages"][-1]["content"]
        
        # !!!!!!!! uncomment for better performance, uses openai
        # response = openai_client.chat.completions.create(
        #     model="gpt-4o-mini"
        #     ,

        messages=[{"role": "user", "content": f"""
You are an agent router. Decide if the following message requires
an emotional/therapist response or a logical/technical response.
Respond ONLY with 'therapist' or 'logical'.

User message: {last_message}
"""}]
        # !!!!!!!! uncomment the below for better performance (uses open aii)
        # ,
        #     temperature=0.0,
        #     max_tokens=10,
        # )

        # next_agent_name = response.choices[0].message.content.strip().lower()
        # if next_agent_name not in agents:
        #     next_agent_name = "logical"  # fallback
        # return agents[next_agent_name]

        reply = llm.invoke(messages)
        next_agent_name = reply.content.strip().lower()

        if next_agent_name not in agents:
            next_agent_name = "logical"  # fallback
        return agents[next_agent_name]

# ---- Therapist Agent ----
class TherapistAgent(BaseAgent):
    def respond(self):
        last_message = self.state["messages"][-1]
        messages = [
            {"role": "system",
             "content": """You are a compassionate therapist. Focus on emotions, validate feelings, ask thoughtful questions."""},
            {"role": "user", "content": last_message["content"]}
        ]
        reply = llm.invoke(messages)
        self.add_message("assistant", reply.content)
        return {"messages": [{"role": "assistant", "content": reply.content}]}

# ---- Logical Agent ----
class LogicalAgent(BaseAgent):
    def respond(self):
        last_message = self.state["messages"][-1]
        messages = [
            {"role": "system",
             "content": """You are a logical assistant. Focus only on facts and information. Be direct."""},
            {"role": "user", "content": last_message["content"]}
        ]
        reply = llm.invoke(messages)
        self.add_message("assistant", reply.content)
        return {"messages": [{"role": "assistant", "content": reply.content}]}

# ---- Multi-Agent Chatbot ----
class MultiAgentChatbot:
    def __init__(self):
        self.agents = {
            "therapist": TherapistAgent("therapist"),
            "logical": LogicalAgent("logical")
        }
        self.current_agent = self.agents["therapist"]

    def run(self):
        print("Type 'bye' to quit.")
        while True:
            user_input = input("Message: ")
            if user_input.lower() == "exit":
                print("Bye")
                break

            # Add user message to all agents' states
            for agent in self.agents.values():
                agent.add_message("user", user_input)

            # Use OpenAI to decide which agent should respond
            self.current_agent = self.current_agent.decide_next_agent(self.agents)

            # Agent responds
            response = self.current_agent.respond()
            last_reply = response["messages"][-1]["content"]
            print(f"{self.current_agent.name.title()} Agent: {last_reply}")

# ---- Run the chatbot ----
if __name__ == "__main__":
    bot = MultiAgentChatbot()
    bot.run()
