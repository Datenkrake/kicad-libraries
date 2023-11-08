from typing import List, Optional, Set, Dict
from sqlmodel import Field, SQLModel, Relationship, JSON, Column, Integer, String, Boolean, DateTime, Float, Enum
from datetime import datetime

class KicadComponent(SQLModel, table=True):
    #__tablename__ = "kicadcomponent"
    id: Optional[str] = Field(default=None, primary_key=True, column="Part ID")
    Symbols: str
    Footprints: str
    MFR: str
    MPN: str
    LCSC: str
    Value: str
    # create "Part ID"  property
