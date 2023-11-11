
import sqlite3
import json


def query_jlcparts(jlc_pid: str):
    # connect to the database
    con = sqlite3.connect("cache.sqlite3")
    cursor = con.cursor()
    # get the column names from the table
    cursor.execute(f"PRAGMA table_info(components)")
    columns = cursor.fetchall()
    # get the row from the table that matches the jlcpid
    statement = f"SELECT * FROM components WHERE lcsc = '{jlc_pid[1:]}'"
    cursor.execute(statement)
    values = cursor.fetchall()
    # build a dictionary from the result of the query above and the column names in columns
    result = [dict(zip([column[1] for column in columns], value)) for value in values]
    try:
        # parse the extra field as json
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