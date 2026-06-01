from sqlalchemy import create_engine
from model.base import Base

class Repository():

    def __init__(self):
        self.engine = create_engine("sqlite:///livros.db", echo=True)
        Base.metadata.create_all(self.engine)