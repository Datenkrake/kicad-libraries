from typing import List, Optional, Set, Dict
from sqlmodel import Field, SQLModel, Relationship, JSON, Column, Integer, String, Boolean, DateTime, Float, Enum
from datetime import datetime

class KicadComponent(SQLModel, table=True):
    #__tablename__ = "kicadcomponent"
    id: Optional[int] = Field(default=None, primary_key=True)
    Symbols: str
    Footprints: str
    MFR: str
    MPN: str
    LCSC: str
    Value: str
    # create "Part ID"  property
    def on_before_insert(self):
        self.id = self.LCSC + "_" + self.MPN
        return self.id
        