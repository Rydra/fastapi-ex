from fastapi import APIRouter

router = APIRouter()


@router.get("/foo/", tags=["foos"])
async def print_foo():
    return "foo"
