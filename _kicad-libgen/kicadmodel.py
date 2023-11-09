from typing import List, Optional, Set, Dict
from sqlmodel import Field, SQLModel, Relationship, JSON, Column, Integer, String, Boolean, DateTime, Float, Enum
from datetime import datetime

class KicadComponent(SQLModel, table=True):
    #__tablename__ = "kicadcomponent"
    id: Optional[str] = Field(default=None, primary_key=True)

    Symbols: str
    Footprints: str
    MFR: str
    MPN: str
    LCSC: str
    Value: str
    Datasheet: str
    Description: str
    Stock: str
    Category: str
    Subcategory: str
    Price: str


    



    
