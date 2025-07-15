from fastapi import APIRouter, Query
from services.indexer import Indexer
from typing import List, Dict

router = APIRouter()

@router.get("/search", response_model=List[Dict])
async def search_files(q: str = Query(..., min_length=1)):
    indexer = Indexer()
    results = indexer.search(q)
    return results