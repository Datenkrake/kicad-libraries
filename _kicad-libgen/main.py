#%%
import subprocess
import json
import requests
import os
from sqlmodel import SQLModel, Session, select
import kicadmodel
from sqlalchemy.orm.exc import NoResultFound
from database import engine, create_db_and_tables
import sqlite3
import pprint as pp

class KiCADlibGen:
    # take a jlc_pid as input and generate a KiCAD lib file by calling JLC2KiCadlib with the jlc_pid
    #def query_item(self, jlc_pid, options = []):
    def query_item(self, jlc_pid, options = []):
        '''
        take a JLCPCB part # and create the according component's kicad's library

        positional arguments:
        JLCPCB_part_#         list of JLCPCB part # from the components you want to create

        options:
        -h, --help            show this help message and exit
        -dir OUTPUT_DIR       base directory for output library files
        --no_footprint        use --no_footprint if you do not want to create the footprint
        --no_symbol           use --no_symbol if you do not want to create the symbol
        -symbol_lib SYMBOL_LIB
                                set symbol library name, default is "default_lib"
        -symbol_lib_dir SYMBOL_LIB_DIR
                                Set symbol library path, default is "symbol" (relative to OUTPUT_DIR)
        -footprint_lib FOOTPRINT_LIB
                                set footprint library name, default is "footprint"
        -models [{STEP,WRL} ...]
                                Select the 3D model you want to use. Default is STEP. 
                                If both are selected, only the STEP model will be added to the footprint (the WRL model will still be generated alongside the STEP model). 
                                If you do not want any model to be generated, use the --models without arguments
        -model_dir MODEL_DIR  Set directory for storing 3d models, default is "packages3d" (relative to FOOTPRINT_LIB)
        --skip_existing       use --skip_existing if you want do not want to replace already existing footprints and symbols
        -model_base_variable MODEL_BASE_VARIABLE
                                use -model_base_variable if you want to specify the base path of the 3D model using a path variable
        -logging_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                                set logging level. If DEBUG is used, the debug logs are only written in the log file if the option --log_file is set
        --log_file            use --log_file if you want logs to be written in a file
        --version             Print versin number and exit

        exemple use : 
                python3 JLC2KiCad_lib.py C1337258 C24112 -dir My_lib -symbol_lib My_Symbol_lib --no_footprint
        return: response from JLC2KiCadLib stdout, productModel, brandNameEn, catalogName, lcsc_url
        '''
        self.jlc_pid = jlc_pid
        # buuild the command
        command = [
            "python3",  # The Python interpreter
            "-m", "JLC2KiCadLib.JLC2KiCadLib",  # Your script file
            jlc_pid,  # List of JLCPCB part #
            # append the options
            *options
        ]
        # Run the script as a subprocess
        jlc2kicadlib = subprocess.run(command, capture_output=True)

        # check if the command was successful
        if jlc2kicadlib.returncode != 0:
            # if not, return the error
            return jlc2kicadlib.stderr.decode("utf-8")

       # # get additional info from LCSC
        lcsc_url = f"https://wmsc.lcsc.com/wmsc/search/global?keyword={jlc_pid}"
        # print (lcsc_url) formatted as image in markdown
        # ![lcsc_url](lcsc_url) to embedd the image in markdown

        image_url = f"https://easyeda.com/api/products/{jlc_pid}/svgs"
        # image = requests.get(image_url).content["result"]["svg"]
        # save the image to a file named after the jlc_pid

        response = requests.get(lcsc_url)
       # # check if the request was successful
        if response.status_code != 200:
            return response.content.decode("utf-8")
           
       # if not, return the error
        else:
            lcsc_data = json.loads(response.content.decode("utf-8"))
            jlc2kicadlib = [jlc2kicadlib, lcsc_data["result"]["tipProductDetailUrlVO"], image_url, lcsc_url]


        # split the stdout from the JLC2KiCadLib API into a list of lines
        info = jlc2kicadlib[0].stdout.decode("utf-8").split("\n")

        # find the line that contains the symbol name
        symbol = [s for s in info if "creating symbol" in s]
        # if at least one line contains the symbol name
        if len(symbol) > 0:
            symbol = symbol[0]
            symbol = symbol[symbol.find("creating symbol ")+len("creating symbol "):symbol.find(" in")]
            symbol = symbol[:-2]
            symbol = f'{symbol}:{symbol}'
        else:
            symbol = None

        symbolfile = [s for s in info if f'{symbol} in ' in s]
        if len(symbolfile) > 0:
            symbolfile = symbolfile[0]
            symbolfile = symbolfile[symbolfile.find(f"{symbol} in ")+len(f"{symbol} in "):]
        else:
            symbolfile = None

        footprint = [s for s in info if ".kicad_mod" in s]
        if len(footprint) > 0:
            footprint = footprint[0]
            footprint = footprint[footprint.find("created ")+len("created "):-1].split("/")[-1]
            footprintfilename = footprint
            footprint = footprint[:-len('.kicad_mod')]
            footprint = f'footprint:{footprint}'
            #os.system(f"mv JLC2KiCad_lib/footprint/{footprint}.kicad_mod JLC2KiCad_lib/Library.pretty/{footprint}.kicad_mo")
        else:
            footprint = None

        model = [s for s in info if "STEP model created at " in s]
        if len(model) > 0:
            model = model[0]
            model = model[model.find("STEP model created at ")+len("STEP model created at "):].split("/")[-1]
        if (jlc2kicadlib[1] is not None):

            # create a dict with the data from the JLC2KiCadLib API
            thingdict = {
                "LCSC_PID": jlc2kicadlib[1]["productCode"],
                "manufacturer": jlc2kicadlib[1]["brandNameEn"],
                "manufacturer_part_number": jlc2kicadlib[1]["productModel"],
                "LCSC Component Type": jlc2kicadlib[1]["catalogName"],
                "LCSC Symbol": symbol,
                "LCSC Symbol File": symbolfile,
                "LCSC Footprint": footprint,
                "LCSC 3D Model": model
            }
            
            # STEP model created at JLC2KiCad_lib/footprint/packages3d/LQFP-44_L10.0-W10.0-P0.80-LS12.0-BL.step\n
            # added JLC2KiCad_lib/footprint/packages3d/LQFP-44_L10.0-W10.0-P0.80-LS12.0-BL.step to footprint\n
            # created 'JLC2KiCad_lib/footprint/LQFP-44_L10.0-W10.0-P0.80-LS12.0-BL.kicad_mod'\n
            
            # move .kicad_mod files from JLC2KiCad_lib to JLC2KiCad_lib/Library.pretty

        else:
            thingdict = None

        return thingdict

def query_jlcparts(jlc_pid: str):
    con = sqlite3.connect("cache.sqlite3")
    cursor = con.cursor()
    cursor.execute(f"PRAGMA table_info(components)")
    columns = cursor.fetchall()
    statement = f"SELECT * FROM components WHERE lcsc = '{jlc_pid[1:]}'"
    cursor.execute(statement)
    values = cursor.fetchall()
    # build a dictionary from the result of the query above and the column names in columns
    result = [dict(zip([column[1] for column in columns], value)) for value in values]
    try:
        extra = json.loads(result[0]["extra"])

        # create dict from result
        thingdict = {
            "LCSC_PID": extra['number'],
            'Datasheet': result[0]['datasheet'],
            'Description': result[0]['description'],
            'Stock': result[0]['stock'],
            'Category': extra['category']['name1'],
            'Subcategory': extra['category']['name2'],
            'Price': extra['prices'][0]['price'],
        }
    except:
        thingdict = None

    return thingdict

def update_symlibtable(thingdict: dict):
    name = thingdict["LCSC Symbol"].split(":")[0]
    type = "KiCad"
    file = thingdict["LCSC Symbol"]+".kicad_sym"
    visible = "hidden"
    uri = "${KICAD7_SYMBOL_DIR}/"+file
    # Specify the line you want to add
    new_line = f'(lib (name "{name}")(type "{type}")(uri "{uri}")(options "")(descr "")({visible}))'
    #new_line = '(lib (name "{name}")(type "{type}")(uri "'+"${KICAD7_SYMBOL_DIR}"+'/{file}")(options "")(descr "")({visible}))'
    #new_line = '(lib (name "NewLibrary")(type "KiCad")(uri "${KICAD7_SYMBOL_DIR}/new_library.kicad_sym")(options "")(descr "New library description")(disabled))'

    # Read the existing file
    with open('sym-lib-table', 'r') as file:
        lines = file.readlines()

    # Find the last enclosing bracket
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == ')':
            # Insert the new line before the last bracket
            lines.insert(i, new_line + '\n')
            break

    # Add the last bracket back
    #lines.append(')')

    # Write the updated content back to the file
    with open('sym-lib-table', 'w') as file:
        file.writelines(lines)


kicadlibgen = KiCADlibGen()

def query_lcsc(jlc_pid: str):
    lcsc_data = kicadlibgen.query_item(jlc_pid=jlc_pid, options="")
    if lcsc_data is None:
        return {"message": "not found"}
    kicad_component = kicadmodel.KicadComponent()
    kicad_component.LCSC = lcsc_data["LCSC_PID"]
    kicad_component.MFR = lcsc_data["manufacturer"]
    kicad_component.MPN = lcsc_data["manufacturer_part_number"]
    kicad_component.Value = lcsc_data["LCSC Component Type"]
    kicad_component.Symbols = lcsc_data["LCSC Symbol"]
    kicad_component.Footprints = lcsc_data["LCSC Footprint"]

    jlcparts_data = query_jlcparts(jlc_pid)
    if jlcparts_data is not None:
        kicad_component.Datasheet = jlcparts_data["Datasheet"]
        kicad_component.Description = jlcparts_data["Description"]
        kicad_component.Stock = jlcparts_data["Stock"]
        kicad_component.Category = jlcparts_data["Category"]
        kicad_component.Subcategory = jlcparts_data["Subcategory"]
        kicad_component.Price = jlcparts_data["Price"]

    kicad_component.uuid = f'{lcsc_data["manufacturer"]}_{lcsc_data["manufacturer_part_number"]}_{lcsc_data["LCSC_PID"]}'

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

    update_symlibtable(lcsc_data)
    return kicad_component
    

def do_the_thing(jlc_pid: str):
    # check if the jlc_pid is a comma separated list
    if "," in jlc_pid:
        # split the list into a list of jlc_pid
        jlc_pid = jlc_pid.split(",")
        # loop through the list of jlc_pid
        for jlc_pid in jlc_pid:
            # query the jlc_pid
            p = query_lcsc(jlc_pid)
            pp.pprint(p)

    else:
        # query the jlc_pid
        p = query_lcsc(jlc_pid)
        pp.pprint(p)

    
#%%
# make callable from the command line
if __name__ == "__main__":
    import argparse
    # if no db exists, create it
    #SQLModel.metadata.create_all(engine)
    parser = argparse.ArgumentParser(description="Query the LCSC database")
    parser.add_argument("jlc_pid", type=str, help="JLCPCB part #")
    args = parser.parse_args()
    do_the_thing(args.jlc_pid)


#%%
# create_db_and_tables()
# result = query_lcsc("C6653")
# result
# # %%