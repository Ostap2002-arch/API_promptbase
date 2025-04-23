import sys
from os.path import dirname, abspath
from typing import List
from fastapi import APIRouter, HTTPException

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from data_extractor import  get_url_category, get_info_prompt
from schemas import Prompt

router = APIRouter()


@router.get("/{category}/{N}", response_model=List[Prompt])
def get_prompt(category: str, N: int = 3):
    url = get_url_category(category)
    return get_info_prompt(url, N=N)
