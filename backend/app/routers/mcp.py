
import asyncio
import uuid
import logging
from typing import Dict
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.mcp_service import MCPService
from app.schemas.mcp import JSONRPCRequest, JSONRPCResponse, JSONRPCError

router = APIRouter()
logger = logging.getLogger(__name__)

# Session Management
# Map: sessionId -> asyncio.Queue
sessions: Dict[str, asyncio.Queue] = {}

async def event_generator(session_id: str, queue: asyncio.Queue):
    """
    Generator for SSE. Yields messages from the queue.
    """
    try:
        # เพิ่ม padding ให้ proxy flush ทันที
        yield f": {' ' * 8192}\n\n"

        endpoint_uri = f"/mcp/message?sessionId={session_id}"
        yield f"event: endpoint\ndata: {endpoint_uri}\n\n"
        
        # padding ก้อนสอง — บังคับ flush หลัง endpoint
        yield f": {' ' * 8192}\n\n"

        while True:
            try:
                # Wait for message with timeout for keepalive
                message = await asyncio.wait_for(queue.get(), timeout=15.0)
                yield f"data: {message}\n\n"
                # padding หลังทุก message
                yield f": {' ' * 1024}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield ": ping\n\n"
    except asyncio.CancelledError:
        logger.info(f"SSE Session {session_id} disconnected")
        sessions.pop(session_id, None)

@router.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    queue = asyncio.Queue()
    sessions[session_id] = queue
    
    logger.info(f"New MCP session created: {session_id}")
    
    return StreamingResponse(
        event_generator(session_id, queue),
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
    request: JSONRPCRequest, 
    sessionId: str = Query(...), 
    db: Session = Depends(get_db)
):
    if sessionId not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Initialize service
    service = MCPService(db)
    queue = sessions[sessionId]
    
    try:
        response = None
        
        if request.method == "initialize":
            response = JSONRPCResponse(
                id=request.id, 
                result={
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "cctv-mcp",
                        "version": "1.0.0"
                    }
                }
            )
        
        elif request.method == "notifications/initialized":
            # Notifications do not require a response in JSON-RPC
            # But we can log it
            logger.info(f"Session {sessionId} initialized")
            return JSONResponse(status_code=202, content={"status": "accepted"})
            
        elif request.method == "tools/list":
            tools = [
                {
                    "name": "check_camera_status",
                    "description": "Check real-time status of cameras by location search (pings IP)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "Location name or search term"}
                        },
                        "required": ["location"]
                    }
                },
                {
                    "name": "find_cameras_by_location",
                    "description": "Find cameras by location from DB (no ping)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string", "description": "Location name"}
                        },
                        "required": ["location"]
                    }
                }
            ]
            response = JSONRPCResponse(id=request.id, result={"tools": tools})
            
        elif request.method == "tools/call":
            params = request.params
            if not params:
                 response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32602, message="Invalid params"))
            else:
                tool_name = params.get("name")
                tool_args = params.get("arguments", {})
                
                if tool_name == "check_camera_status":
                    location = tool_args.get("location")
                    if not location:
                         response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32602, message="Missing location"))
                    else:
                        result = await service.check_camera_status(location)
                        response = JSONRPCResponse(id=request.id, result={"content": [{"type": "text", "text": str(result)}]})
                    
                elif tool_name == "find_cameras_by_location":
                    location = tool_args.get("location")
                    if not location:
                         response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32602, message="Missing location"))
                    else:
                        result = service.find_cameras_by_location(location)
                        response = JSONRPCResponse(id=request.id, result={"content": [{"type": "text", "text": str(result)}]})
                else:
                    response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32601, message="Method not found"))
        
        else:
            response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32601, message="Method not found"))

        if response:
            # Send response through SSE stream
            await queue.put(response.model_dump_json())
            return JSONResponse(status_code=202, content={"status": "accepted"})
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        error_response = JSONRPCResponse(id=request.id, error=JSONRPCError(code=-32000, message=str(e)))
        await queue.put(error_response.model_dump_json())
        return JSONResponse(status_code=202, content={"status": "accepted"})

    return JSONResponse(status_code=202, content={"status": "accepted"})
