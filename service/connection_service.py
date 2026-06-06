from sqlalchemy import delete, insert, select, update

from model.device import Device
from model.connection import Connection 
from repository.repository import Repository

class ConnectionService():

    def __init__(self):
        self.repository = Repository()
    
    def create_connection(self, connection: Connection):
        if connection.source_id == connection.destination_id:
            raise ValueError("O dispositivo de origem não pode ser igual ao de destino.")

        with self.repository.engine.begin() as conn:
            # INSERT INTO CONNECTION (type, source_id, destination_id) VALUES (Connection.type, Connection.source_id, Connection.destination_id)
            query = insert(Connection).values(
                type = connection.type,
                source_id = connection.source_id,
                destination_id = connection.destination_id
            ).returning(Connection.id)
            
            result = conn.execute(query)
            connection.id = result.scalar()
            return connection
    
    def list_connection(self):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM CONNECTION
            query = select(Connection)
            result = conn.execute(query)
            return [Connection(**row) for row in result.mappings()]
    
    def select_connection(self, id: int):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM CONNECTION WHERE ID = connection.id
            query = select(Connection).where(Connection.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Connection(**row) if row else None
    
    def update_connection(self, connection: Connection):
        old = self.select_connection(connection.id)

        if not old:
            return
        
        with self.repository.engine.begin()as conn:
            # UPDATE * FROM CONNECTION WHERE CONNECTION.ID = id VALUES (Connection.type, Connection.source_id, Connection.destination_id)
            query = update(Connection).where(Connection.id == connection.id).values(
                type = connection.type or old.type,
                source_id = connection.source_id or old.source_id,
                destination_id = connection.destination_id or old.destination_id
            )
            conn.execute(query)
            
            return self.select_connection(connection.id)
    
    def delete_connection(self, id: int):
        with self.repository.engine.begin() as conn:
            # DELETE * FROM CONNECTION WHERE CONNECTION.ID = id
            query = delete(Connection).where(Connection.id == id)
            conn.execute(query)

