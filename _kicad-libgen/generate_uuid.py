import sqlite3

def generate_uuid(kicad_component):
    # connect to the database
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