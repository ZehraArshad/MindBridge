import os, asyncio, urllib.parse, traceback, json
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.prompts import ChatPromptTemplate
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import Tool
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

# ---- Initialize Groq LLM ----
llm = init_chat_model(
    model=os.getenv("LLM_MODEL", "gemma2-9b-it"),
    model_provider=os.getenv("LLM_PROVIDER", "groq"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.0,
    max_tokens=8000,
)

# ---- Therapist Tool ----
async def therapist_tool(message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a compassionate therapist."},
        {"role": "user", "content": message},
    ]
    reply = llm.invoke(messages)
    return reply.content

# ---- Logical Tool ----
async def logical_tool(message: str) -> str:
    messages = [
        {"role": "system", "content": "You are a logical assistant. Be direct."},
        {"role": "user", "content": message},
    ]
    reply = llm.invoke(messages)
    return reply.content

# ---- Build Prompt ----
def build_prompt(coral_tools_description, agent_tools_description):
    return ChatPromptTemplate.from_messages([
        (
             "system",
            f"""
            You are a router agent that decides whether a user message 
            needs an emotional (therapist) or logical response. 

            Workflow:
            1. Use `user-input-request` to ask the user: "How can I assist you today?".
            2. Wait for their reply via `user-input-respond`.
            3. Classify response as emotional or logical.
            4. Call therapist_tool or logical_tool.
            5. Send your reply back using `send_message` (so Coral UI sees it).
            6. Always loop back to step 1.
            7. You MUST NEVER finish the chain.

            Coral tools: {coral_tools_description}
            Agent tools: {agent_tools_description}
            """
        ),
        ("placeholder", "{agent_scratchpad}"),
    ])

# ---- Create Agent ----
async def create_agent(coral_tools, agent_tools):
    coral_tools_description = "\n".join(t.name for t in coral_tools)
    agent_tools_description = "\n".join(t.name for t in agent_tools)
    combined_tools = coral_tools + agent_tools
    prompt = build_prompt(coral_tools_description, agent_tools_description)
    agent = create_tool_calling_agent(llm, combined_tools, prompt)
    return AgentExecutor(agent=agent, tools=combined_tools, verbose=True)

# ---- Main Loop ----
# ---- Main Loop ----
# ---- Main Loop ----
async def main():
    base_url = os.getenv("CORAL_SSE_URL")
    agentID = os.getenv("CORAL_AGENT_ID")

    coral_params = {
        "agentId": agentID,
        "agentDescription": "Router agent that decides between therapist and logical responses."
    }

    query_string = urllib.parse.urlencode(coral_params)
    CORAL_SERVER_URL = f"{base_url}?{query_string}"
    print(f"Connecting to Coral Server: {CORAL_SERVER_URL}")

    client = MultiServerMCPClient(
        connections={
            "coral": {
                "transport": "sse",
                "url": CORAL_SERVER_URL,
                "timeout": 300,
                "sse_read_timeout": 300,
            }
        }
    )
    
    # 🔹 Grab all Coral tools
    coral_tools = await client.get_tools()
    print("\n=== Available coral tools ===")
    for t in coral_tools:
        print(" -", t.name, "|", getattr(t, "description", None))
        print("=============================\n")
    

    # 🔹 Extract the specific ones we’ll use
    send_message = next(t for t in coral_tools if t.name == "coral_send_message")
    wait_mentions = next(t for t in coral_tools if t.name == "coral_wait_for_mentions")
    

    # Therapist / logical tools
    agent_tools = [
        Tool(
            name="therapist_tool",
            func=None,
            coroutine=therapist_tool,
            description="Respond with a compassionate, therapist-style message."
        ),
        Tool(
            name="logical_tool",
            func=None,
            coroutine=logical_tool,
            description="Respond with a logical, direct message."
        ),
    ]

    agent_executor = await create_agent(coral_tools, agent_tools)

    # 🔹 Bootstrap first message
    # 🔹 Bootstrap first user prompt using Coral UI
    # Grab DevMode chatbox tools
    request_question = next(t for t in coral_tools if t.name == "request-question")
    answer_question = next(t for t in coral_tools if t.name == "answer-question")

# Ask first question (Studio shows chatbox)
    await request_question.arun({"question": "Hi! How can I assist you today?"})

# Wait for answer
    mention_event = await answer_question.arun({})
    user_input = mention_event.get("answer", "").strip()

# 🔹 Conversation loop
    while True:
        print("\n Waiting for user input in Coral UI...")
        
        # Wait for user response from chatbox
        mention_event = await wait_input.arun({})
        
        # Extract user text
        try:
            user_input = mention_event["answer"].strip()
        except Exception:
            user_input = ""
        
        if not user_input:
            continue
        
        print(f"\nUser: {user_input}")
        if user_input.lower() in {"quit", "exit"}:
            break

        # Route response through your agent
        result = await agent_executor.ainvoke({"input": user_input})
        reply = result["output"]
        print(f"Agent: {reply}")

        # Reply in Coral UI
        await send_message.arun({"message": reply})
        
        # Prompt user again
        await request_input.arun({"question": "Anything else I can help with?"})


if __name__ == "__main__":
    asyncio.run(main())
