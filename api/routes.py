from fastapi import APIRouter, Query, Request
from typing import List, Dict

router = APIRouter()

@router.get("/search", response_model=List[Dict])
async def search_files(request: Request, q: str = Query(..., min_length=1)):
    results = request.app.state.indexer.search(q)
    return results