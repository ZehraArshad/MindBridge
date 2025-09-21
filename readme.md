## Description

MindBridge is an agentic software built on Coral that routes user messages to emotional or logical AI responses, creating an interactive chat experience for personalized support and reasoning.

## How to run

### Configure envs

- One in root (for server)
- one inside reception
### Adding Dependencies


uv add requirements.txt
uv pip install -r requirements.txt 

- [pyproject.toml](coral-server\agents\reception\pyproject.toml)
- [requirements.txt](requirements.txt)
- [agent without server](coral-server\agents\reception\coral_agent.py)


### Agent

```
cd coral-server
cd agents\reception
main.py

```

### Running Coral Server 

```
cd coral server

 ./gradlew run
```
### Running studio 

```
npx @coral-protocol/coral-studio      
```