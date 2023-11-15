import sqlite3
import json

def update_db_json():
    conn = sqlite3.connect('_kicad-libgen/db.sqlite3')  # Replace with your actual database file name
    cursor = conn.cursor()

    # Execute a SELECT query to fetch data from your table
    cursor.execute('SELECT * FROM kicadcomponent')  # Replace with your actual table name
    rows = cursor.fetchall()

    # Get the column names from the cursor description
    columns = [desc[0] for desc in cursor.description]

    # Close the database connection
    conn.close()

    # Convert the data to a list of dictionaries
    data = [dict(zip(columns, row)) for row in rows]

    # Write the data to a JSON file
    with open('db.json', 'w') as json_file:
        json.dump(data, json_file, indent=2)