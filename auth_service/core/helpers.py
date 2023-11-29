from fastapi.responses import JSONResponse
from pydantic import BaseModel


def json_exception(msg: str, status_code: int, **kwargs) -> JSONResponse:
    return JSONResponse(content={"error": msg}, status_code=status_code, **kwargs)