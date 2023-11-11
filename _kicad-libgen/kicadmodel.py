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

    def to_dict(self):
        return {
            "id": self.id,
            "Symbols": self.Symbols,
            "Footprints": self.Footprints,
            "MFR": self.MFR,
            "MPN": self.MPN,
            "LCSC": self.LCSC,
            "Value": self.Value,
            "Datasheet": self.Datasheet,
            "Description": self.Description,
            "Stock": self.Stock,
            "Category": self.Category,
            "Subcategory": self.Subcategory,
            "Price": self.Price,
            "uuid": self.uuid,
            "value1": self.value1,
            "value2": self.value2,
            "value3": self.value3,
            "value4": self.value4
        }

    



    
