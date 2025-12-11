from pydantic import BaseModel, Field
from typing import List, Optional

class Entry(BaseModel):
    category: str = Field(...)
    amount: float = Field(..., ge=0)
    date: str = Field(...)
    description: Optional[str] = None

class FarmerData(BaseModel):
    farmer_name: str
    crop_name: str
    season: str
    total_acres: float
    total_production: Optional[float] = None
    sowing_date: str
    harvest_date: str
    location: str
    expenses: List[Entry]
    incomes: List[Entry]
