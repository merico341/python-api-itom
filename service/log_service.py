from sqlalchemy import insert, select

from datetime import datetime

from model.log import Log
from repository.repository import Repository

class LogService():

    def __init__(self):
        self.repository = Repository()
    
    def create_log(self, log: Log):
        
        if log.date_hour is None:
            log.date_hour = datetime.now()
        
        with self.repository.engine.begin() as conn:
            # INSERT INTO log (operation, status, description, device_id, user_id, date_hour) VALUES (?, ?, ?, ?, ?, ?) RETURNING log.id
            query = insert(Log).values(
                operation = log.operation,
                status = log.status,
                description = log.description or None,
                device_id = log.device_id,
                user_id = log.user_id,
                date_hour = log.date_hour
            ).returning(Log.id)
            
            result = conn.execute(query)
            log.id = result.scalar()
            return log
    
    def list_log(self):
        with self.repository.engine.connect() as conn:
            # SELECT log.id, log.operation, log.status, log.description, log.device_id, log.user_id, log.date_hour FROM log
            query = select(Log)
            result = conn.execute(query)
            return [Log(**row) for row in result.mappings()]
    
    def list_log_by_user(self, user_id):
        with self.repository.engine.connect() as conn:
            # INSERT INTO log (operation, status, description, device_id, user_id, date_hour) VALUES (?, ?, ?, ?, ?, ?) RETURNING log.id
            query = select(Log).where(Log.user_id == user_id)
            result = conn.execute(query)
            return [Log(**row) for row in result.mappings()]
    
    def list_log_by_device(self, device_id):
        with self.repository.engine.connect() as conn:
            # SELECT log.id, log.operation, log.status, log.description, log.device_id, log.user_id, log.date_hour FROM log WHERE log.device_id = ?
            query = select(Log).where(Log.device_id == device_id)
            result = conn.execute(query)
            return [Log(**row) for row in result.mappings()]
    
    def select_log(self, id):
        with self.repository.engine.connect() as conn:
            # SELECT log.id, log.operation, log.status, log.description, log.device_id, log.user_id, log.date_hour FROM log WHERE log.id = ?
            query = select(Log).where(Log.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Log(**row) if row else None
    