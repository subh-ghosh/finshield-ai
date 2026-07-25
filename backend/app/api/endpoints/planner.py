import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.agent.graph import get_agent_executor
from langchain_core.messages import HumanMessage

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    customer_id: str
    thread_id: str = "default_thread"


@router.post("/chat")
async def chat_with_planner(request: ChatRequest):
    agent_executor = get_agent_executor()

    async def event_generator():
        try:
            config = {"configurable": {"thread_id": request.thread_id}}
            input_message = HumanMessage(content=request.message)

            # Use streaming
            # The custom graph yields state updates after each node
            for event in agent_executor.stream(
                {"messages": [input_message], "customer_id": request.customer_id},
                config=config,
            ):
                # event is a dict mapping node_name -> node_state
                for node_name, node_state in event.items():
                    # Send an event about which node just completed
                    yield f"data: {json.dumps({'type': 'status', 'content': f'Completed: {node_name}'})}\n\n"

                    # If this is the recommendation node, extract the final response
                    if node_name == "generate_recommendation":
                        final_rec = node_state.get("final_recommendation")
                        if final_rec:
                            # Also extract planner timeline to send as steps
                            timeline = node_state.get("planner_timeline", [])
                            steps = [
                                {"tool": log["tool"], "result": log["result"]}
                                for log in timeline
                            ]

                            # Final message
                            messages = node_state.get("messages", [])
                            final_msg = messages[-1].content if messages else "Done."

                            final_response = {
                                "type": "final",
                                "response": final_msg,
                                "recommendation": final_rec,
                                "intermediate_steps": steps,
                            }
                            yield f"data: {json.dumps(final_response)}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            error_response = {
                "type": "error",
                "content": f"Error executing planner: {str(e)}",
            }
            yield f"data: {json.dumps(error_response)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
