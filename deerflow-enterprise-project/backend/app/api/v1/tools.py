from fastapi import APIRouter

router = APIRouter(
    prefix="/tools",
    tags=["tools"],
    responses={404: {"description": "Not found"}},
)

@router.get("/list")
async def list_tools():
    """List available tools"""
    return {
        "tools": [
            {"name": "browser", "description": "Web browsing capability"},
            {"name": "calculator", "description": "Math calculation tool"}
        ]
    }