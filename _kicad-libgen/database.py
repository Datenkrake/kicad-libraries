from sqlmodel import SQLModel, create_engine, Session
#import os

DATABASE_URL = "sqlite:///_kicad-libgen/db.sqlite3"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
#     # delete the database file if it exists
#     if os.path.exists("db.sqlite3"):
#         os.remove("db.sqlite3")
#     # delete all tables from the database
#     SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine) 