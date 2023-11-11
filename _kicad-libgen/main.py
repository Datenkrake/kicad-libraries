from sqlmodel import Session
import kicadmodel
from sqlalchemy.orm.exc import NoResultFound
from database import engine
import pprint as pp

from libgen import query_item
from jlcquery import query_jlcparts
from symlibtable import update_symlibtable
from kicadmod import update_kicadmod_model



def do_the_thing(jlc_pid: str):
    # query the kicad library from JLC using JLC2KiCad
    lcsc_data = query_item(jlc_pid=jlc_pid, options="")
    if lcsc_data is None:
        return {"message": "not found"}
    # create a kicad component from the data
    kicad_component = kicadmodel.KicadComponent()
    kicad_component.LCSC = lcsc_data["LCSC_PID"]
    kicad_component.MFR = lcsc_data["manufacturer"]
    kicad_component.MPN = lcsc_data["manufacturer_part_number"]
    kicad_component.Value = lcsc_data["LCSC Component Type"]
    kicad_component.Symbols = lcsc_data["LCSC Symbol"]
    kicad_component.Footprints = lcsc_data["LCSC Footprint"]
    kicad_component.uuid = f'{lcsc_data["manufacturer"]}_{lcsc_data["manufacturer_part_number"]}_{lcsc_data["LCSC_PID"]}'
    # fix model path in footprint file to make it relative
    update_kicadmod_model(lcsc_data['LCSC Footprint'][len('footprint:'):]+'.kicad_mod')

    # query the jlc parts database
    jlcparts_data = query_jlcparts(jlc_pid)
    if jlcparts_data is not None:
        # update the kicad component with the jlc parts data
        kicad_component.Datasheet = jlcparts_data["Datasheet"]
        kicad_component.Description = jlcparts_data["Description"]
        kicad_component.Stock = jlcparts_data["Stock"]
        kicad_component.Category = jlcparts_data["Category"]
        kicad_component.Subcategory = jlcparts_data["Subcategory"]
        kicad_component.Price = jlcparts_data["Price"]

    # add the component to the database
    with Session(engine) as session:
        try:
            existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.LCSC == kicad_component.LCSC).one()
            
            # Component found, update attributes
            for key, value in kicad_component.dict().items():
                if value is not None:
                    setattr(existing_component, key, value)
            session.commit()
            session.refresh(existing_component)
            kicad_component = existing_component
            
        except NoResultFound:
            # Component not found, add it
            session.add(kicad_component)
            # Commit changes
            session.commit()
            # Refresh the component
            session.refresh(kicad_component)

    # update the symlibtable
    update_symlibtable(lcsc_data)

    return kicad_component
    


    
#%%
# make callable from the command line
if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Query the LCSC database")
    parser.add_argument("jlc_pid", type=str, help="JLCPCB part #")
    args = parser.parse_args()

    # list with results
    results = []
    jlc_pid = args.jlc_pid
    if "," in jlc_pid:
        # split the list into a list of jlc_pid
        jlc_pid = jlc_pid.split(",")
        # loop through the list of jlc_pid
        for jlc_pid in jlc_pid:
            # query the jlc_pid
            p = do_the_thing(jlc_pid)
            results.append(p)

    else:
        # query the jlc_pid
        p = do_the_thing(jlc_pid)
        results.append(p)

    return results
