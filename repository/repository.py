from dotenv import dotenv_values
from sqlalchemy import create_engine
from model.base import Base

env = dotenv_values(".env")

db_adrss = env["DB_ADRSS"]
db_name = env["DB_NAME"]
db_user = env["DB_USER"]
db_passwd = env["DB_PASSWD"]
db_port = env["DB_PORT"]

class Repository():
    
    def __init__(self):
        DATABASE_URL = f"postgresql+psycopg2://{db_user}:{db_passwd}@{db_adrss}:{db_port}/{db_name}"
        self.engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(self.engine)