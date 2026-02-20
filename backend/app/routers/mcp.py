import asyncio
import uuid
import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.requests import Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.mcp import JSONRPCError, JSONRPCResponse
from app.services.mcp_service import MCPService

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[Any] = None          # Optional — notifications มี id เป็น None

# ---------------------------------------------------------------------------
# Tool definitions (static — ย้ายมาไว้นอก handler เพื่อ reuse)
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS = [
    {
        "name": "check_camera_status",
        "description": (
            "Check real-time online/offline status of CCTV cameras "
            "by searching name, id, or location. Pings the camera IP."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Camera name, id, or location keyword (e.g. 'E1', 'ประตูหน้า')"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "find_cameras_by_location",
        "description": (
            "Find cameras by location from the database. "
            "Returns stored status without pinging."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location keyword to search (e.g. 'อาคาร E')"
                }
            },
            "required": ["location"]
        }
    }
]

# ---------------------------------------------------------------------------
# Session store
# ---------------------------------------------------------------------------

sessions: Dict[str, asyncio.Queue] = {}

# ---------------------------------------------------------------------------
# SSE helpers
# ---------------------------------------------------------------------------

PROXY_FLUSH_PADDING = " " * 8192

async def event_generator(session_id: str, queue: asyncio.Queue, request: Request):
    try:
        # Force proxy flush
        yield f": {PROXY_FLUSH_PADDING}\n\n"

        # Announce message endpoint
        yield f"event: endpoint\ndata: /mcp/message?sessionId={session_id}\n\n"

        # Second flush to ensure endpoint line is delivered
        yield f": {PROXY_FLUSH_PADDING}\n\n"

        while True:
            if await request.is_disconnected():
                break
            try:
                message = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {message}\n\n"
                yield f": {' ' * 1024}\n\n"   # flush after each message
            except asyncio.TimeoutError:
                yield ": ping\n\n"             # keepalive

    except asyncio.CancelledError:
        pass
    finally:
        sessions.pop(session_id, None)
        logger.info(f"SSE session closed: {session_id}")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    sessions[session_id] = asyncio.Queue()
    logger.info(f"SSE session created: {session_id}")

    return StreamingResponse(
        event_generator(session_id, sessions[session_id], request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Content-Type-Options": "nosniff",
            "Transfer-Encoding": "chunked",
        }
    )


@router.post("/message")
async def handle_message(
    rpc: JSONRPCRequest,
    sessionId: str = Query(...),
    db: Session = Depends(get_db)
):
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    service = MCPService(db)

    try:
        response = await _dispatch(rpc, service, sessionId)
    except Exception as exc:
        logger.exception(f"Unhandled error in session {sessionId}")
        response = JSONRPCResponse(
            id=rpc.id,
            error=JSONRPCError(code=-32000, message=str(exc))
        )

    if response is None:
        return JSONResponse(status_code=202, content={"status": "accepted"})

    # ส่งกลับทาง HTTP body โดยตรง (MCPClient รองรับ hybrid mode อยู่แล้ว)
    return JSONResponse(
        status_code=200,
        content=response.model_dump()
    )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

async def _dispatch(
    rpc: JSONRPCRequest,
    service: MCPService,
    session_id: str
) -> Optional[JSONRPCResponse]:
    """Route JSON-RPC method to the correct handler. Returns None for notifications."""

    method = rpc.method

    if method == "initialize":
        return JSONRPCResponse(
            id=rpc.id,
            result={
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cctv-mcp", "version": "1.0.0"}
            }
        )

    if method == "notifications/initialized":
        logger.info(f"Session initialized: {session_id}")
        return None  # notifications ไม่ต้องตอบกลับ

    if method == "tools/list":
        return JSONRPCResponse(id=rpc.id, result={"tools": TOOL_DEFINITIONS})

    if method == "tools/call":
        return await _handle_tool_call(rpc, service)

    return JSONRPCResponse(
        id=rpc.id,
        error=JSONRPCError(code=-32601, message=f"Method not found: {method}")
    )


async def _handle_tool_call(
    rpc: JSONRPCRequest,
    service: MCPService
) -> JSONRPCResponse:
    params = rpc.params or {}
    tool_name: str = params.get("name", "")
    tool_args: dict = params.get("arguments", {})

    if not tool_name:
        return JSONRPCResponse(
            id=rpc.id,
            error=JSONRPCError(code=-32602, message="Missing tool name")
        )

    try:
        if tool_name == "check_camera_status":
            location = tool_args.get("location", "").strip()
            if not location:
                return JSONRPCResponse(
                    id=rpc.id,
                    error=JSONRPCError(code=-32602, message="Missing required argument: location")
                )
            result = await service.check_camera_status(location)
            return _text_response(rpc.id, result)

        if tool_name == "find_cameras_by_location":
            location = tool_args.get("location", "").strip()
            if not location:
                return JSONRPCResponse(
                    id=rpc.id,
                    error=JSONRPCError(code=-32602, message="Missing required argument: location")
                )
            result = service.find_cameras_by_location(location)
            return _text_response(rpc.id, result)
            
    except Exception as e:
        logger.exception(f"Error executing tool {tool_name}: {e}")
        return JSONRPCResponse(
            id=rpc.id,
            error=JSONRPCError(code=-32000, message=f"Internal Error: {str(e)}")
        )

    return JSONRPCResponse(
        id=rpc.id,
        error=JSONRPCError(code=-32601, message=f"Unknown tool: {tool_name}")
    )


def _text_response(rpc_id: Any, data: Any) -> JSONRPCResponse:
    """Wrap tool result as MCP text content block."""
    import json
    text = json.dumps(data, ensure_ascii=False, indent=2) if not isinstance(data, str) else data
    return JSONRPCResponse(
        id=rpc_id,
        result={"content": [{"type": "text", "text": text}]}
    )