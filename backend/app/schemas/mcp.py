from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field

class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Any] = None
    id: Optional[Any] = None

class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[JSONRPCError] = None
    id: Optional[Union[str, int]] = None

class CheckCameraStatusParams(BaseModel):
    location: str

class FindCamerasParams(BaseModel):
    location: str
