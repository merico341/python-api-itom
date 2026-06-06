from sqlalchemy import insert, select

from datetime import datetime

from model.log import Log
from repository.repository import Repository

class LogService():

    def __init__(self):
        self.repository = Repository()
    
    def create_log(self, log: Log):
        has_device = bool(log.device_id)
        has_user = bool(log.user_id)
        
        if has_device == has_user:
            raise ValueError("O log deve conter obrigatoriamente ou o id do dispositivo ou o id do usuário (apenas 1).")
        
        if log.date_hour is None:
            log.date_hour = datetime.now()
        
        with self.repository.engine.begin() as conn:
            # INSERT INTO LOG () VALUES ()
            query = insert(Log).values(
                operation = log.operation,
                status = log.status,
                description = log.description if hasattr(log, 'description') else None,
                device_id = log.device_id,
                user_id = log.user_id,
                date_hour = log.date_hour
            ).returning(Log.id)
            
            result = conn.execute(query)
            log.id = result.scalar()
            return log
    
    def list_log(self):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM LOG
            query = select(Log)
            result = conn.execute(query)
            return [Log(**row) for row in result.mappings()]
    
    def select_log(self, id):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM LOG
            query = select(Log).where(Log.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Log(**row) if row else None
    