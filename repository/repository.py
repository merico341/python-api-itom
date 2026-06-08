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
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Repository, cls).__new__(cls)
            
            DATABASE_URL = "postgresql://admin:mpJml3248LlNQ1WCTAhFjSYPID04xA2W@dpg-d8jdc9kvikkc73bgood0-a.oregon-postgres.render.com/banco_xl8w"
            
            cls._instance.engine = create_engine(
                DATABASE_URL,
                pool_size=10,   
                max_overflow=20,
                pool_pre_ping=True
            )
            
            Base.metadata.create_all(cls._instance.engine)
            
        return cls._instance