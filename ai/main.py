
#%% 
import asyncio
from typing import Dict, Any

from langgraph.graph import Graph  # type: ignore
from langchain.chat_models import ChatOpenAI  # type: ignore
import base64
import json
from apis.services.image import (
    generate_image_1d as _generate_image_1d,
    generate_image as _generate_image_4d,
    generate_image_3D as _generate_image_3d,
    generate_transect_image as _generate_transect_image,
)

from apis.models.requests import (
    GenerateImageRequest1D,
    GenerateImageRequest4D,
    GenerateImageRequest3D,
    GenerateImageRequestTransect,
)


# -----------------------------
# Simple asynchronous ReAct agent with LangGraph
# -----------------------------

PROMPT_TEMPLATE = (
    """You are an AI agent that follows the ReAct (Reason + Act) paradigm.\n"
    "You have access to the following tools:\n"
    "- `Search`: general web search.\n"
    "- `GenerateImage1D`: generate a 1-D profile plot. Accepts JSON matching `GenerateImageRequest1D`.\n"
    "- `GenerateImage4D`: generate a 2-D heat-map from 4-D data (time, depth, lat, lon). Accepts JSON matching `GenerateImageRequest4D`.\n"
    "- `GenerateImage3D`: generate a 3-D visualisation. Accepts JSON matching `GenerateImageRequest3D`.\n"
    "- `GenerateTransectImage`: generate a transect heat-map between two points. Accepts JSON matching `GenerateImageRequestTransect`.\n\n"
    "When you want to use a tool, respond *exactly* with:\n"
    "<ToolName>: <JSON arguments>\n\n"
    "When you have the final answer, respond with:\n"
    "FINAL: <your answer here>\n\n"
    "Previous scratchpad (what you have thought/done so far):\n{scratchpad}\n\n"
    "User question: {user_input}\n"
    """
)

# ---------------------------------------------------------------------------
# Mock async search tool -----------------------------------------------------
# ---------------------------------------------------------------------------

async def mock_search(query: str) -> str:
    """A dummy async search function to emulate tool usage."""
    # In real life, replace this with an actual async HTTP request.
    await asyncio.sleep(0.1)  # simulate IO latency
    return f"[Mock search results for '{query}']"

# ---------------------------------------------------------------------------
# Async wrappers around image generation services ---------------------------
# ---------------------------------------------------------------------------


async def generate_image_1d_tool(params_json: str) -> str:
    """Generate 1-D image and return base64-encoded PNG."""
    params_dict = json.loads(params_json)
    params = GenerateImageRequest1D(**params_dict)
    img_bytes = _generate_image_1d(params)
    return base64.b64encode(img_bytes).decode("utf-8")


async def generate_image_4d_tool(params_json: str) -> str:
    """Generate 4-D (lat, lon, depth, time) heat-map image."""
    params_dict = json.loads(params_json)
    params = GenerateImageRequest4D(**params_dict)
    img_bytes = _generate_image_4d(params)
    return base64.b64encode(img_bytes).decode("utf-8")


async def generate_image_3d_tool(params_json: str) -> str:
    """Generate 3-D image and return base64-encoded PNG."""
    params_dict = json.loads(params_json)
    params = GenerateImageRequest3D(**params_dict)
    img_bytes = _generate_image_3d(params)
    return base64.b64encode(img_bytes).decode("utf-8")


async def generate_transect_image_tool(params_json: str) -> str:
    """Generate a transect image between two geographic points."""
    params_dict = json.loads(params_json)
    params = GenerateImageRequestTransect(**params_dict)
    img_bytes = _generate_transect_image(params)
    return base64.b64encode(img_bytes).decode("utf-8")

# ---------------------------------------------------------------------------
# Agent graph construction ---------------------------------------------------
# ---------------------------------------------------------------------------


from typing import Any as _AnyType  # for type annotation flexibility


def build_react_graph() -> _AnyType:
    """Construct and return an async ReAct agent graph."""

    chat_llm: Any = ChatOpenAI(temperature=0.0, model_name="gpt-3.5-turbo")

    # Mapping of tool names to callables -----------------------------------
    available_tools = {
        "Search": mock_search,
        "GenerateImage1D": generate_image_1d_tool,
        "GenerateImage4D": generate_image_4d_tool,
        "GenerateImage3D": generate_image_3d_tool,
        "GenerateTransectImage": generate_transect_image_tool,
    }

    graph: Graph = Graph()

    # 1) THINK + ACT ---------------------------------------------------------
    async def think_act(state: Dict[str, Any]) -> Dict[str, Any]:
        """LLM decides next action (Search or FINAL)."""
        scratchpad: str = state.get("scratchpad", "")
        user_input: str = state["user_input"]

        prompt = PROMPT_TEMPLATE.format(user_input=user_input, scratchpad=scratchpad)

        llm_response: str = str(await chat_llm.apredict(prompt))
        state["llm_response"] = llm_response.strip()

        # Very naive parsing --------------------------------------------------
        # Check if response is a tool invocation
        invoked_tool = None
        tool_args: str = ""
        for tool_name in available_tools:
            prefix = f"{tool_name}:"
            if llm_response.startswith(prefix):
                invoked_tool = tool_name
                tool_args = llm_response[len(prefix) :].strip()
                break

        if invoked_tool:
            state["action"] = invoked_tool
            state["tool_args"] = tool_args
        elif llm_response.startswith("FINAL:"):
            state["action"] = "FINAL"
            state["answer"] = llm_response[len("FINAL:") :].strip()
        else:
            # If the model responds unexpectedly, we treat it as final.
            state["action"] = "FINAL"
            state["answer"] = llm_response
        return state

    # 2) TOOL CALL -----------------------------------------------------------
    async def call_tool(state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected tool and record the result in scratchpad."""
        tool_name: str = state["action"]
        tool_input: str = state.get("tool_args", "")

        # Call the tool ------------------------------------------------------
        result: Any = await available_tools[tool_name](tool_input)

        # Record tool invocation in scratchpad ------------------------------
        scratchpad = state.get("scratchpad", "")
        preview = str(result)[:200] + ("..." if len(str(result)) > 200 else "")
        scratchpad += f"{tool_name}({tool_input}) -> {preview}\n"
        state["scratchpad"] = scratchpad
        # Optionally, store result if needed by LLM in future iterations
        state["last_tool_result"] = result
        return state

    # 3) Routing logic -------------------------------------------------------
    def router(state: Dict[str, Any]):
        """Route to tool node if a tool was selected."""
        if state.get("action") in available_tools:
            return "tool"
        return None  # Terminate if not a tool action (i.e., FINAL)

    # Register nodes + edges --------------------------------------------------
    graph.add_node("react", think_act)
    graph.add_node("tool", call_tool)

    graph.set_entry_point("react")

    # react -> (tool | END)
    graph.add_conditional_edges("react", router)

    # tool -> react (loop back after tool execution)
    graph.add_edge("tool", "react")

    return graph.compile()

# ---------------------------------------------------------------------------
# Helper: run the agent ------------------------------------------------------
# ---------------------------------------------------------------------------

async def run_agent(question: str):
    agent_graph = build_react_graph()
    final_state = await agent_graph.ainvoke({"user_input": question})
    return final_state.get("answer", "No answer produced.")

# ---------------------------------------------------------------------------
# CLI entrypoint -------------------------------------------------------------
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    q = "What is the temperature of the ocean at 100m depth in the North Atlantic Ocean?"
    answer = asyncio.run(run_agent(q))
    print("\n=== Agent answer ===")
    print(answer)
