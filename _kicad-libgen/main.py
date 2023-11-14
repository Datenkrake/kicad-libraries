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

    con = sqlite3.connect("_kicad-libgen/db.sqlite3")
    cursor = con.cursor()
    # select all components with no uuid using sqlite3
    cursor.execute("SELECT * FROM kicadcomponent WHERE uuid IS NULL")
    values = cursor.fetchall()
    # generate a uuid for each component with no uuid with schema uuid = f"B3D{component[0]:06x}"
    for component in values:
        # generate new uuid
        cursor.execute(f"UPDATE kicadcomponent SET uuid = 'B3D{component[0]:06x}' WHERE id = {component[0]}")
        con.commit()
        # add the uuid to kicad_component
        kicad_component.uuid = f"B3D{component[0]:06x}"

    return kicad_component
    
def read_github_issue(repository, issue_number):
    # Get the GitHub token from the environment variable
    token = os.environ.get('GH_TOKEN')

    # Create a Github object using the token
    g = Github(token)

    # Access the repository
    repo = g.get_repo(repository)

    try:
        # Get the issue by number
        issue = repo.get_issue(issue_number)
        issue_json = issue.raw_data
        # drop empty lines from the issue
        issue_body = json.dumps(issue_json, indent=2)

        return issue_body

    except Exception as e:
        print(f"Error: {e}")


    
#%%
# make callable from the command line
if __name__ == "__main__":
    # parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Query the LCSC database")
    parser.add_argument("issue_number", type=int, help="Github Issue Number")
    args = parser.parse_args()
    #print(args)
    # list with results
    results = []
    #jlc_pid = args.jlc_pid

    # Specify the repository and issue number
    repository_name = "Datenkrake/kicad-libraries"
    issue_number = args.issue_number

    # Read the GitHub issue
    issue = read_github_issue(repository_name, issue_number)

    # if "," in jlc_pid:
    #     # split the list into a list of jlc_pid
    #     jlc_pid = jlc_pid.split(",")
    #     # strip whitespace from each jlc_pid
    #     jlc_pid = [j.strip() for j in jlc_pid]
    #     # loop through the list of jlc_pid
    #     for jlc_pid in jlc_pid:
    #         # query the jlc_pid
    #         p = do_the_thing(jlc_pid)
    #         results.append(p)

    # else:
    #     # query the jlc_pid
    #     p = do_the_thing(jlc_pid)
    #     results.append(p)

    # # convert each KicadComponent object in the list to a dictionary
    # results_dicts = [result.to_dict() for result in results]

    # results_string = ""
    # for results_dict in results_dicts:
    #     # convert the list of dictionaries to a string
    #     for key, value in results_dict.items():
    #         results_string += f"{key}: {value} <br>"

    # results_string = shlex.quote(results_string)

    # print(results_string)
    print(f"::set-output name=script-output::{issue}")

