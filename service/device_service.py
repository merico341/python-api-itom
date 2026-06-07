from sqlalchemy import delete, insert, select, update

from model.device import Device
from repository.repository import Repository
from service.log_service import LogService, Log

class DeviceService():

    def __init__(self):
        self.repository = Repository()
        self.log_service = LogService()


    def create_device(self, device: Device, user_id_executante):
        with self.repository.engine.begin() as conn:
            # INSERT INTO device (name, type, ip, user_id) VALUES (?, ?, ?, ?) RETURNING device.id
            query = insert(Device).values(
                name = device.name,
                type = device.type,
                ip = device.ip or None,
                user_id = device.user_id or None,
            ).returning(Device.id)
            
            result = conn.execute(query)
            device.id = result.scalar()

        self.log_service.create_log(Log(
            operation="CREATE_DEVICE",
            status="SUCCESS",
            description=f"Dispositivo '{device.name}' (ID: {device.id}) cadastrado com sucesso.",
            user_id=user_id_executante
        ))
        return device
    
    def list_devices_by_type(self, type):
        with self.repository.engine.connect() as conn:
            # SELECT device.id, device.name, device.type, device.ip, device.user_id FROM device WHERE device.type = ?
            query = select(Device).where(Device.type == type)
            result = conn.execute(query)
            return [Device(**row) for row in result.mappings()]
        
    def list_devices(self):
        with self.repository.engine.connect() as conn:
            # SELECT device.id, device.name, device.type, device.ip, device.user_id FROM device
            query = select(Device)
            result = conn.execute(query)
            return [Device(**row) for row in result.mappings()]

    def select_device(self, id):
        with self.repository.engine.connect() as conn:
            # SELECT device.id, device.name, device.type, device.ip, device.user_id FROM device WHERE device.id = ?
            query = select(Device).where(Device.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Device(**row) if row else None

    def update_device(self, device: Device, user_id_executante):
        old = self.select_device(device.id)

        if not old:
            raise ValueError(f"Dispositivo com ID {device.id} não encontrado.")
        
        with self.repository.engine.begin() as conn:
            # UPDATE device SET name=?, type=?, ip=?, user_id=? WHERE device.id = ?
            query = update(Device).where(Device.id == device.id).values(
                name = device.name or old.name,
                type = device.type or old.type,
                ip = device.ip or old.ip,
                user_id = device.user_id or old.user_id
            )
            conn.execute(query)
        
        self.log_service.create_log(Log(
            operation="UPDATE_DEVICE",
            status="SUCCESS",
            description=f"Dispositivo ID {device.id} atualizado.",
            user_id=user_id_executante
        ))
        return self.select_device(device.id)
    
    def delete_device(self, id, user_id_executante):
        old = self.select_device(id)
        if not old:
            raise ValueError(f"Dispositivo com ID {id} não encontrado.")
        
        with self.repository.engine.begin() as conn:
            # DELETE FROM device WHERE device.id = ?
            query = delete(Device).where(Device.id == id)
            conn.execute(query)
        
        self.log_service.create_log(Log(
            operation="DELETE_DEVICE",
            status="SUCCESS",
            description=f"Dispositivo '{old.name}' (ID: {id}) foi removido permanentemente.",
            user_id=user_id_executante
        ))