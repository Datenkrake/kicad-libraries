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
    Datasheet: str
    Description: str
    Stock: str
    Category: str
    Subcategory: str
    Price: str
    uuid: str
    value1: str
    value2: str
    value3: str
    value4: str

    def on_create(self):
        self.id = None  # It will be auto-incremented

    def on_before_insert(self):
        return self


    



    
