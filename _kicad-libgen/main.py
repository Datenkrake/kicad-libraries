from sqlmodel import Session
import kicadmodel
from sqlalchemy.orm.exc import NoResultFound
from database import engine
import pprint as pp
import base64
import json
import shlex
import sqlite3
import os
from github import Github

from libgen import query_item
from jlcquery import query_jlcparts
from symlibtable import update_symlibtable
from kicadmod import update_kicadmod_model
from symclean import clean_symbol
from values import find_values
from generate_uuid import generate_uuid
from custom_component import create_custom_component, update_custom_component
from read_issue import read_github_issue

def do_the_thing(jlc_pid: str, overwrite: bool):
    # query the kicad library from JLC using JLC2KiCad
    if overwrite is True:
        lcsc_data = query_item(jlc_pid=jlc_pid, options="")
    else:
        lcsc_data = query_item(jlc_pid=jlc_pid, options="--skip_existing")
    if lcsc_data is None:
        return {"message": "not found"}
    # create a kicad component from the data
    kicad_component = kicadmodel.KicadComponent()
    kicad_component.LCSC = lcsc_data["LCSC_PID"]
    kicad_component.MFR = lcsc_data["manufacturer"]
    kicad_component.MPN = lcsc_data["manufacturer_part_number"]
    #kicad_component.Value = lcsc_data["LCSC Component Type"]
    kicad_component.Symbols = lcsc_data["LCSC Symbol"]
    kicad_component.Footprints = lcsc_data["LCSC Footprint"]
    # fix model path in footprint file to make it relative
    if lcsc_data['LCSC Footprint'] is not None:
        update_kicadmod_model(lcsc_data['LCSC Footprint'][len('footprint:'):]+'.kicad_mod')
    if lcsc_data['LCSC Symbol'] is not None:
        clean_symbol(lcsc_data['LCSC Symbol'].split(':')[1])

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
        # find the values in the description
        values = find_values(jlcparts_data)
        # update the kicad component with the values
        if values is not None:
            kicad_component.Value = ', '.join([str(v) for v in [values['value1'], values['value2'], values['value3'], values['value4']] if v is not None])
            kicad_component.value1 = values["value1"]
            kicad_component.value2 = values["value2"]
            kicad_component.value3 = values["value3"]
            kicad_component.value4 = values["value4"]


    # add the component to the database
    with Session(engine) as session:
        try:
            existing_component = session.query(kicadmodel.KicadComponent).filter(kicadmodel.KicadComponent.LCSC == kicad_component.LCSC).one()
            
            # Component found, update attributes
            for key, value in kicad_component.dict().items():
                if value is not None:
                    # if overwrite is True, overwrite the existing value
                    if overwrite is True:
                        setattr(existing_component, key, value)
                    # if overwrite is False, only overwrite the existing value if it is None
                    if overwrite is False and getattr(existing_component, key) is None:
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
    update_symlibtable(lcsc_data["LCSC Symbol"].split(':')[0])
    # write uuid to the database
    kicad_component = generate_uuid(kicad_component)

    return kicad_component
    
    
#%%
# make callable from the command line
if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Query the LCSC database")
    parser.add_argument("issue_number", type=int, help="Github Issue Number")
    args = parser.parse_args()
    # list with results
    results = []

    # Specify the repository and issue number
    repository_name = "Datenkrake/kicad-libraries"
    issue_number = args.issue_number
    # Read the GitHub issue
    print(f"Reading GitHub issue {issue_number} from {repository_name}")
    issue_dict = read_github_issue(repository_name, issue_number)
    # if issue_dict mpn or mfr is _No response_, set to None
    if issue_dict['mpn'] == "_No response_":
        issue_dict['mpn'] = None
    if issue_dict['mfr'] == "_No response_":
        issue_dict['mfr'] = None
    if "," in issue_dict['pid']:
        print("Multiple pids found")
        # split pid into a list of pids
        pids = issue_dict['pid'].split(",")
        # strip whitespace from each pid
        pids = [pid.strip() for pid in pids]
        # loop through the list of pids
        for pid in pids:
            # if pid does not contain B3D
            if "B3D" not in pid:
                # query the pid
                p = do_the_thing(pid, issue_dict['overwrite'])
                p = update_custom_component(pid, issue_dict)
                results.append(p)
            if "B3D" in pid:
                # query the pid
                p = update_custom_component(pid, issue_dict)
                results.append(p)
    else:
        print("Single pid found")
        # if pid does not contain B3D
        if "B3D" not in issue_dict['pid']:
            # query the pid
            p = do_the_thing(issue_dict['pid'], issue_dict['overwrite'])
            p = update_custom_component(issue_dict['pid'], issue_dict)
            results.append(p)
        if "B3D" in issue_dict['pid']:
            # query the pid
            p = update_custom_component(issue_dict['pid'], issue_dict)
            results.append(p)

    # if without_lcsc is True
    # check that mfr and mpn are not None
    if issue_dict['without_lcsc'] is True and issue_dict['mfr'] is not None and issue_dict['mpn'] is not None:
        print("without_lcsc is True")
        p = create_custom_component(issue_dict)
        #p = update_custom_component(p.uuid, issue_dict)
        # add the component to the list of results as a dictionary
        results.append(p)

    # convert each KicadComponent object in the list to a dictionary
    results_dicts = [result.to_dict() for result in results]

    results_string = ""
    for results_dict in results_dicts:
        # convert the list of dictionaries to a string
        for key, value in results_dict.items():
            results_string += f"{key}: {value} <br>"

    results_string = shlex.quote(results_string)

    print(results_string)
    print(f"::set-output name=script-output::{results_string}")

