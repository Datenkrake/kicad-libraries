import sqlite3
from jlcquery import query_jlcparts


def main():
    # connect to the database
    con = sqlite3.connect("cache.sqlite3")
    cursor = con.cursor()

    # connect to the database _kicad-libgen/db.sqlite3
    con2 = sqlite3.connect("_kicad-libgen/db.sqlite3")
    cursor2 = con2.cursor()

    # get the column names from the table
    cursor2.execute(f"PRAGMA table_info(kicadcomponent)")
    columns = cursor2.fetchall()

    # for each component in db.sqlite3 table kicadcomponent
    cursor2.execute("SELECT * FROM kicadcomponent")
    values = cursor2.fetchall()

    result = [dict(zip([column[1] for column in columns], value)) for value in values]

    for component in result:
        # get the lcsc pid
        lcsc = component['LCSC']
        # get the jlcdata
        jlcdata = query_jlcparts(lcsc)
        # update component['Price'] and component['Stock'] in db.sqlite with jlcdata['stock'] and jlcdata['price']
        if jlcdata is not None:
            component['Price'] = jlcdata['Price']
            component['Stock'] = jlcdata['Stock']
            # update the database
            cursor2.execute(f"UPDATE kicadcomponent SET Price = '{component['Price']}', Stock = '{component['Stock']}' WHERE LCSC = '{lcsc}'")
            con2.commit()


if __name__ == '__main__':
    main()