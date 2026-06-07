from sqlalchemy import delete, insert, select, update

from model.connection import Connection 
from repository.repository import Repository
from service.log_service import LogService, Log
from util.log_enum_util import LogOperation, LogStatus


class ConnectionService():

    def __init__(self):
        self.repository = Repository()
        self.log_service = LogService()
    
    def create_connection(self, connection: Connection, user_id_executante):
        if connection.source_id == connection.destination_id:
            raise ValueError("O dispositivo de origem não pode ser igual ao de destino.")

        with self.repository.engine.begin() as conn:
            # INSERT INTO connection (type, source_id, destination_id) VALUES (?, ?, ?) RETURNING connection.id
            query = insert(Connection).values(
                type = connection.type,
                source_id = connection.source_id,
                destination_id = connection.destination_id
            ).returning(Connection.id)
            
            result = conn.execute(query)
            connection.id = result.scalar()
            
        self.log_service.create_log(Log(
            operation=LogOperation.CREATE,
            status=LogStatus.SUCCESS,
            description=f"Conexão de rede ID {connection.id} criada entre Dispositivo {connection.source_id} e {connection.destination_id}.",
            user_id=user_id_executante
        ))
        return connection
    
    def list_connection(self):
        with self.repository.engine.connect() as conn:
            # SELECT connection.id, connection.type, connection.source_id, connection.destination_id FROM connection    
            query = select(Connection)
            result = conn.execute(query)
            return [Connection(**row) for row in result.mappings()]
    
    def list_connection_by_source(self, device_id):
        with self.repository.engine.connect() as conn:
            # SELECT connection.id, connection.type, connection.source_id, connection.destination_id FROM connection WHERE connection.source_id = ?
            query = select(Connection).where(Connection.source_id == device_id)
            result = conn.execute(query)
            return [Connection(**row) for row in result.mappings()]
    
    def list_connection_by_destination(self, device_id):
        with self.repository.engine.connect() as conn:
            # SELECT connection.id, connection.type, connection.source_id, connection.destination_id FROM connection WHERE connection.destination_id = ?
            query = select(Connection).where(Connection.destination_id == device_id)
            result = conn.execute(query)
            return [Connection(**row) for row in result.mappings()]
    
    def select_connection(self, id: int):
        with self.repository.engine.connect() as conn:
            # SELECT connection.id, connection.type, connection.source_id, connection.destination_id FROM connection WHERE connection.id = ?
            query = select(Connection).where(Connection.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Connection(**row) if row else None
    
    def update_connection(self, connection: Connection, user_id_executante):
        old = self.select_connection(connection.id)

        if not old:
            raise ValueError(f"Conexão com ID {connection.id} não encontrada.")
            
        novo_source = connection.source_id or old.source_id
        novo_destination = connection.destination_id or old.destination_id
        if novo_source == novo_destination:
            raise ValueError("A atualização geraria uma conexão do dispositivo com ele mesmo.")
        
        with self.repository.engine.begin()as conn:
            # UPDATE connection SET type=?, source_id=?, destination_id=? WHERE connection.id = ?
            query = update(Connection).where(Connection.id == connection.id).values(
                type = connection.type or old.type,
                source_id = connection.source_id or old.source_id,
                destination_id = connection.destination_id or old.destination_id
            )
            conn.execute(query)
            
        self.log_service.create_log(Log(
            operation=LogOperation.UPDATE,
            status=LogStatus.SUCCESS,
            description=f"Conexão de rede ID {connection.id} modificada.",
            user_id=user_id_executante
        ))
        return self.select_connection(connection.id)
    
    def delete_connection(self, id: int, user_id_executante: int):
        old = self.select_connection(id)
        if not old:
            raise ValueError(f"Conexão com ID {id} não encontrada.")

        with self.repository.engine.begin() as conn:
            # DELETE FROM connection WHERE connection.id = ?
            query = delete(Connection).where(Connection.id == id)
            conn.execute(query)

        self.log_service.create_log(Log(
            operation=LogOperation.DELETE,
            status=LogStatus.SUCCESS,
            description=f"Conexão de rede ID {id} entre os dispositivos {old.source_id} e {old.destination_id} foi removida.",
            user_id=user_id_executante
        ))
