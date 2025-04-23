import sys
from os.path import dirname, abspath
from typing import List
from fastapi import APIRouter, HTTPException

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from data_extractor import get_info
from schemas import Prompt

router = APIRouter()


@router.get("/{category}/{N}", response_model=List[Prompt])
def get_prompt(category: str, N: int = 3):
    if category not in ['Models', 'Art', 'Logos', 'Graphics', 'Productivity', 'Marketing', 'Photography', 'Games']:
        raise HTTPException(
            status_code=404,
            detail="Сategory not found",
        )
    return get_info(category=category, N=N)
