from sqlmodel import Session
from database import engine
import kicadmodel
from generate_uuid import generate_uuid
from symlibtable import update_symlibtable
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound



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
     # set the values
    if issue_dict['Symbols'] is not None and issue_dict['Symbols'] != "-":
        kicad_component.Symbols = issue_dict['Symbols']+":"+issue_dict['Symbols']
    else:
        kicad_component.Symbols = None
    if issue_dict['Footprints'] is not None and issue_dict['Footprints'] != "-":
        kicad_component.Footprints = "footprint:"+issue_dict['Footprints']
    else:
        kicad_component.Footprints = None
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
    with Session(engine) as session:
        # get the existing component
        try:
            if pid.startswith("B3D"):
                existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.uuid == pid).one()
                # get existing component uuid from pid and store in existing_component2 variable without using session.query
            else:
                existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.LCSC == pid).one()

            # Component found, update attributes
            for key, value in issue_dict.items():
                # Check for non-empty string
                if value is not None and value != "":
                    setattr(existing_component, key, value)
                elif value == "-":
                    setattr(existing_component, key, None)

            # If Symbols is not None, update symlibtable
            if issue_dict.get('Symbols') is not None:
                update_symlibtable(issue_dict['Symbols'])
            
            session.add(existing_component)
            session.commit()
            session.refresh(existing_component)
        
        except NoResultFound:
            print(f"No record found with uuid={pid}")
        except MultipleResultsFound:
            print(f"Multiple records found with uuid={pid}")


    return existing_component

