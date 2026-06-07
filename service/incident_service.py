from sqlalchemy import delete, insert, select, update, func

from model.incident import Incident
from service.log_service import LogService, Log
from repository.repository import Repository
from util.log_enum_util import LogOperation, LogStatus

class IncidentService():

    def __init__(self):
        self.repository = Repository()
        self.log_service = LogService()
    
    def create_incident(self, incident: Incident):
        with self.repository.engine.begin() as conn:
            # SELECT max(incident.id) AS max_1 FROM incident
            max_id_query = select(func.max(Incident.id))
            max_id = conn.execute(max_id_query).scalar() or 0
            next_number = f"INC{(max_id + 1):05d}"
            
            # INSERT INTO incident (number, title, description, state, priority, caller_id, device_id) VALUES (?, ?, ?, ?, ?, ?, ?) RETURNING id, number, created_at, updated_at
            query = insert(Incident).values(
                number = next_number,
                title = incident.title,
                state = incident.state,
                priority = incident.priority,
                caller_id = incident.caller_id,
                device_id = incident.device_id or None,
                description = incident.description or None
            ).returning(Incident.id, Incident.number, Incident.created_at, Incident.updated_at)
            
            result = conn.execute(query).fetchone()
            
            incident.id = result[0]
            incident.number = result[1]
            incident.created_at = result[2]
            incident.updated_at = result[3]
            
        
        self.log_service.create_log(Log(
            operation=LogOperation.CREATE,
            status=LogStatus.SUCCESS,
            description=f"Incidente {incident.number} criado com sucesso.",
            user_id=incident.caller_id
        ))

        return incident
    
    def list_incident(self):
        with self.repository.engine.connect() as conn:
            # SELECT incident.id, incident.number, incident.title, incident.state, incident.priority, incident.caller_id, incident.created_at, incident.updated_at, incident.description, incident.device_id FROM incident
            query = select(Incident)
            result = conn.execute(query)

            return [Incident(**row) for row in result.mappings()]
    
    def list_incident_by_caller(self, caller_id: int):
        with self.repository.engine.connect() as conn:
            # SELECT incident.id, incident.number, incident.title, incident.state, incident.priority, incident.caller_id, incident.created_at, incident.updated_at, incident.description, incident.device_id FROM incident WHERE incident.caller_id = ?
            query = select(Incident).where(Incident.caller_id == caller_id)
            result = conn.execute(query)

            return [Incident(**row) for row in result.mappings()]

    def select_incident(self, id: int):
        with self.repository.engine.connect() as conn:
            # SELECT incident.id, incident.number, incident.title, incident.state, incident.priority, incident.caller_id, incident.created_at, incident.updated_at, incident.description, incident.device_id FROM incident WHERE incident.id = ?
            query = select(Incident).where(Incident.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Incident(**row) if row else None
    
    def update_incident(self, incident: Incident, user_id_executante: int):
        old = self.select_incident(incident.id)

        if not old:
            return
            
        with self.repository.engine.begin() as conn:
            # UPDATE incident SET title=?, description=?, state=?, priority=?, caller_id=?, device_id=?, updated_at=CURRENT_TIMESTAMP WHERE incident.id = ?
            query = update(Incident).where(Incident.id == incident.id).values(
                title = incident.title or old.title,
                description = incident.description or old.description,
                state = incident.state or old.state,
                priority = incident.priority or old.priority,
                caller_id = incident.caller_id or old.caller_id,
                device_id = incident.device_id or old.device_id
            )
            conn.execute(query)

        self.log_service.create_log(Log(
            operation=LogOperation.UPDATE,
            status=LogStatus.SUCCESS,
            description=f"Incidente {old.number} modificado.",
            user_id=user_id_executante
        ))
            
        return self.select_incident(incident.id)
    
    def delete_incident(self, id: int, user_id_executante):
        old = self.select_incident(id)
        if not old:
            raise ValueError(f"Incidente com ID {id} não encontrado.")
        
        with self.repository.engine.begin() as conn:
            # DELETE FROM incident WHERE incident.id = ?
            query = delete(Incident).where(Incident.id == id)
            conn.execute(query)
        
        self.log_service.create_log(Log(
            operation=LogOperation.DELETE,
            status=LogStatus.SUCCESS,
            description=f"Incidente número {old.number} foi excluído permanentemente.",
            user_id=user_id_executante
        ))