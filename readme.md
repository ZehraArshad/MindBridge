# Session, Rooms, Participants ????

✅ So in short:

Room = container for real-time communication (like a Zoom room).

Participant = a person or agent connected into that room.

### Each participant has:

Tracks → streams of audio, video, or data.

Attributes → metadata (e.g., "role": "doctor", "agent": "triage").

So, when your agent connects, it becomes a participant in the room.

### For local dev, we need to create rooms!!!


### What is session in a Coral? Is that a room?

Session (Coral) = a managed room + extra orchestration (logging, multi-agent, orchestration).

Agents need rooms because without them, there’s no audio/video/data exchange channel.

## Adding agent 

- make main.py that has agent logic
- store the main.py in a folder, folder name must match the one in [registry.toml](registry.toml)
- this registry.toml will later on be used by the server when we do gradlew run

```

coral-protocol/
│
├── server/
│   ├── registry.toml        # Coral Server looks here
│   └── ...
│
└── agents/
    └── reception/
        ├── coral-agent.toml # Defines workers inside reception
        ├── main.py          # Your BasicAgent logic

```

- For each agent:

```
[[local-agent]]
path = "reception"

```
- Prompts are optional

## Making venv
- In the terminal run:
```
python -m venv .venv
.\.venv\Scripts\activate
```

### making project.toml


```
uv init

uv add -r ../../requirements.txt

```
- Don't push venv to github repo

## Installing a package 
- numpy pillow pyyaml are packages
```
<!-- uv pip install numpy pillow pyyaml -->
uv pip install -r requirements.txt
```
- Keep a requirements txt
- Add every package, you install to txt


- if package is not needed uninstall
- check each package direction 


## Structure
```
project-root/
├─ server
    registry.toml                # Coral v1 registry listing local agents
├─ triage/
│  ├─ coral-agent.toml
│  ├─ main.py
│  └─ prompts/...
├─ support/
│  ├─ coral-agent.toml
│  ├─ main.py
├─ billing/
│  ├─ coral-agent.toml
│  ├─ main.py
├─ patient_db/                  # small service + sqlite file
│  ├─ db.py
│  ├─ service.py                # optional tiny FastAPI service
│  └─ patients.sqlite
└─ README.md
```


## Langgraph

### State
- store info that an agent needs to complete a task


### Node
- each node runs a funtion(tool calling, running agent, summarizing text)
- nodes are like steps in AI


### Edges

- connection between nodes
- start - research 
- research - write

### State graph
use state graph to 
- Add nodes
- Connect them with edges
- Define the overall flow
- Compile it into an executable program


### @ToolDecorator

- turn normal python func into a tool that can be used by agent


### Types

- React: (think, decide, use, reflect and repeact)
- Chain of thoughts: explain their reasoning before giving answers
- Agents talk to other agents
- Agents call api directly
- Agents with conditional rules


### registry.toml

- https://discord.com/channels/1346160632096886814/1417808446811672627