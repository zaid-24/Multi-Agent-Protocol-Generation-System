"""
Cerina Protocol Foundry MCP Server

Exposes the multi-agent CBT protocol generation system as an MCP tool.
"""

import asyncio
import httpx
from typing import Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Backend API Configuration
BACKEND_URL = "http://127.0.0.1:8000"

# Create MCP Server
server = Server("cerina-protocol-foundry")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="generate_cbt_protocol",
            description=(
                "Generate a CBT (Cognitive Behavioral Therapy) protocol using Cerina's "
                "multi-agent system. The agents will draft, review for safety/empathy/clinical "
                "quality, and refine the protocol autonomously."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "The user intent for the protocol, e.g., 'Create a sleep hygiene protocol for insomnia'"
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional clinical context or patient notes"
                    },
                    "auto_approve": {
                        "type": "boolean",
                        "description": "If true, auto-approve when agents reach consensus (default: true)",
                        "default": True
                    }
                },
                "required": ["prompt"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name != "generate_cbt_protocol":
        raise ValueError(f"Unknown tool: {name}")
    
    prompt = arguments.get("prompt")
    context = arguments.get("context")
    auto_approve = arguments.get("auto_approve", True)
    
    if not prompt:
        raise ValueError("prompt is required")
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        # 1. Create session
        create_response = await client.post(
            f"{BACKEND_URL}/sessions",
            json={"user_intent": prompt, "user_context": context}
        )
        create_response.raise_for_status()
        session_data = create_response.json()
        session_id = session_data["session_id"]
        status = session_data["status"]
        
        # 2. Poll until terminal state
        max_polls = 60  # 2 minutes max
        poll_interval = 2.0
        
        for _ in range(max_polls):
            if status in ["APPROVED", "FAILED"]:
                break
            
            if status == "AWAITING_HUMAN" and auto_approve:
                # Auto-approve by calling human_approve endpoint
                state_response = await client.get(f"{BACKEND_URL}/sessions/{session_id}/state")
                state_response.raise_for_status()
                state = state_response.json()
                
                current_content = state.get("current_draft", {}).get("content", "")
                
                approve_response = await client.post(
                    f"{BACKEND_URL}/sessions/{session_id}/human_approve",
                    json={
                        "new_content": current_content,
                        "action": "APPROVE_FINAL",
                        "comments": "Auto-approved via MCP"
                    }
                )
                approve_response.raise_for_status()
                result = approve_response.json()
                status = result.get("status", status)
            else:
                await asyncio.sleep(poll_interval)
                state_response = await client.get(f"{BACKEND_URL}/sessions/{session_id}/state")
                state_response.raise_for_status()
                state = state_response.json()
                status = state.get("status", status)
        
        # 3. Fetch final state
        final_state_response = await client.get(f"{BACKEND_URL}/sessions/{session_id}/state")
        final_state_response.raise_for_status()
        final_state = final_state_response.json()
        
        # 4. Build response
        protocol_content = final_state.get("current_draft", {}).get("content", "No protocol generated")
        safety_score = final_state.get("safety_score")
        empathy_score = final_state.get("empathy_score")
        clinical_score = final_state.get("clinical_score")
        iteration_count = final_state.get("iteration", 0)
        final_status = final_state.get("status", "UNKNOWN")
        
        response_text = f"""# CBT Protocol Generation Result

## Status: {final_status}

## Scores
- Safety: {safety_score:.2f if safety_score else 'N/A'}
- Empathy: {empathy_score:.2f if empathy_score else 'N/A'}
- Clinical: {clinical_score:.2f if clinical_score else 'N/A'}

## Iterations: {iteration_count}

## Protocol

{protocol_content}
"""
        
        return [TextContent(type="text", text=response_text)]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
