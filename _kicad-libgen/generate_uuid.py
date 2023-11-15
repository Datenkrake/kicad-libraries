import sqlite3
from sqlmodel import Session
from database import engine
import kicadmodel

def generate_uuid(kicad_component):
    # get the component from the database
    with Session(engine) as session:
        existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.id == kicad_component.id).one()
    # if the component already has a uuid, return it
        if existing_component.uuid is not None:
            return existing_component
        # if the component does not have a uuid, generate one
        if existing_component.uuid is None:
            # set the uuid to 'B3D{component[0]:06x}' where component[0] is the id of the component
            setattr(existing_component, "uuid", f"B3D{existing_component.id:06x}".upper())
            # commit the change
            session.commit()
            session.refresh(existing_component)
            # return the component
    return existing_component
