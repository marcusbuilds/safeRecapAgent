from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
from .agent import run_agent

router = APIRouter()

class AgentRequest(BaseModel):
    user_input: str
    history: list = []  # List of dicts with 'type' and 'content'

class AgentResponse(BaseModel):
    response: str

@router.post("/agent/run", response_model=AgentResponse)
def agent_run(request: AgentRequest):
    # Convert history to LangChain message objects
    history_msgs = []
    for msg in request.history:
        if msg.get('type') == 'human':
            history_msgs.append(HumanMessage(content=msg['content']))
        elif msg.get('type') == 'ai':
            history_msgs.append(AIMessage(content=msg['content']))
    result = run_agent(request.user_input, history_msgs)
    return AgentResponse(response=result.content)
