from sqlmodel import Session
from database import engine
import kicadmodel
from generate_uuid import generate_uuid
from symlibtable import update_symlibtable

def create_custom_component(issue_dict: dict):
    # create kicadcomponent
    kicad_component = kicadmodel.KicadComponent()
    # set the values
    # Symbols: str
    # Footprints: str
    # MFR: str
    # MPN: str
    # LCSC: str
    # Value: str
    # Datasheet: str
    # Description: str
    # Stock: str
    # Category: str
    # Subcategory: str
    # Price: str
    # uuid: str
    # value1: str
    # value2: str
    # value3: str
    # value4: str
    kicad_component.Symbols = issue_dict['Symbols']
    kicad_component.Footprints = issue_dict['Footprints']
    kicad_component.MFR = issue_dict['mfr']
    kicad_component.MPN = issue_dict['mpn']
    kicad_component.LCSC = None
    # kicadmodel.Value = issue_dict['Value']
    kicad_component.Datasheet = issue_dict['Datasheet']
    kicad_component.Description = issue_dict['Description']
    # kicadmodel.Stock = issue_dict['Stock']
    kicad_component.Category = issue_dict['Category']
    kicad_component.Subcategory = issue_dict['Subcategory']
    # kicadmodel.Price = issue_dict['Price']
    kicad_component.value1 = issue_dict['value1']
    kicad_component.value2 = issue_dict['value2']
    kicad_component.value3 = issue_dict['value3']
    kicad_component.value4 = issue_dict['value4']

    with Session(engine) as session:
        session.add(kicad_component)
        session.commit()
        session.refresh(kicad_component)

    kicad_component = generate_uuid(kicad_component)

    return kicad_component


def update_custom_component(pid, issue_dict: dict):
    # create kicadcomponent
    kicad_component = kicadmodel.KicadComponent()

    # set the values
    if issue_dict['Symbols'] is not None and issue_dict['Symbols'] != "-":
        kicad_component.Symbols = issue_dict['Symbols']+":"+issue_dict['Symbols']
    else:
        kicad_component.Symbols = issue_dict['Symbols']
    if issue_dict['Footprints'] is not None and issue_dict['Footprints'] != "-":
        kicad_component.Footprints = "footprint:"+issue_dict['Footprints']
    else:
        kicad_component.Footprints = issue_dict['Footprints']

    kicad_component.MFR = issue_dict['mfr']
    kicad_component.MPN = issue_dict['mpn']
    kicad_component.LCSC = None
    # kicadmodel.Value = issue_dict['Value']
    kicad_component.Datasheet = issue_dict['Datasheet']
    kicad_component.Description = issue_dict['Description']
    # kicadmodel.Stock = issue_dict['Stock']
    kicad_component.Category = issue_dict['Category']
    kicad_component.Subcategory = issue_dict['Subcategory']
    # kicadmodel.Price = issue_dict['Price']
    kicad_component.value1 = issue_dict['value1']
    kicad_component.value2 = issue_dict['value2']
    kicad_component.value3 = issue_dict['value3']
    kicad_component.value4 = issue_dict['value4']

    if kicad_component.Symbols is not None:
        update_symlibtable(issue_dict['Symbols'])

    with Session(engine) as session:
        # get the existing component
        try:
            if pid.startswith("B3D"):
                existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.uuid == pid).one()
            else:
                existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.LCSC == pid).one()
            # Component found, update attributes
            # if the issue_dict value is not None, overwrite the existing value
            # if the issue_dict value is "-", set value to None
            for key, value in kicad_component.dict().items():
                if value is not None and value != "-":
                    setattr(existing_component, key, value)
                if value == "-":
                    setattr(existing_component, key, "")
            session.commit()
            session.refresh(existing_component)
            kicad_component = existing_component
            return kicad_component
        
        except:
            print("Component not found")
            return None
