from sqlalchemy import delete, insert, select, update, func
from model.incident import Incident
from repository.repository import Repository

class IncidentService():

    def __init__(self):
        self.repository = Repository()
    
    def create_incident(self, incident: Incident):
        with self.repository.engine.begin() as conn:
            max_id_query = select(func.max(Incident.id))
            max_id = conn.execute(max_id_query).scalar() or 0
            next_number = f"INC{(max_id + 1):05d}"
            
            # INSERT INTO INCIDENT (number, title, description, state, priority, caller_id, device_id) VALUES (incident.number, incident.title, incident.description, incident.state, incident.priority, incident.caller_id, incident.device_id)
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
            
            return incident
    
    def list_incident(self):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM INCIDENT 
            query = select(Incident)
            result = conn.execute(query)

            return [Incident(**row) for row in result.mappings()]
    
    def select_incident(self, id: int):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM INCIDENT WHERE INCIDENT.id = id
            query = select(Incident).where(Incident.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Incident(**row) if row else None
    
    def update_incident(self, incident: Incident):
        old = self.select_incident(incident.id)

        if not old:
            return
            
        with self.repository.engine.begin() as conn:
            # UPDATE incident SET title=incident.title, description=incident.description, state=incident.state, priority=incident.priority, caller_id=incident.caller_id, device_id=incident.device_id, updated_at=CURRENT_TIMESTAMP WHERE incident.id = incident.id
            query = update(Incident).where(Incident.id == incident.id).values(
                title = incident.title or old.title,
                description = incident.description or old.description,
                state = incident.state or old.state,
                priority = incident.priority or old.priority,
                caller_id = incident.caller_id or old.caller_id,
                device_id = incident.device_id or old.device_id
            )
            conn.execute(query)
            
        return self.select_incident(incident.id)
    
    def delete_incident(self, id: int):
        with self.repository.engine.begin() as conn:
            # DELETE * FROM INCIDENT WHERE INCIDENT.ID = id
            query = delete(Incident).where(Incident.id == id)
            conn.execute(query)