from sqlalchemy import delete, insert, select, update

from model.device import Device
from repository.repository import Repository

class DeviceService():

    def __init__(self):
        self.repository = Repository()

    def create_device(self, device: Device):
        with self.repository.engine.begin() as conn:
            # INSERT INTO DEVICE (name, type, id, user_id) VALUES (Device.name, Device.type, Device.id, Device.user_id)

            query = insert(Device).values(
                name = device.name,
                type = device.type,
                ip = device.ip or None,
                user_id = device.user_id or None,
            )
            conn.execute(query)
    
    def list_devices(self):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM USER
            query = select(Device)
            result = conn.execute(query)
            return [Device(**row) for row in result.mappings()]

    def select_device(self, id):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM USER WHERE ID = device.id
            query = select(Device).where(Device.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return Device(**row) if row else None

    def update_device(self, device: Device):
        old = self.select_device(device.id)

        if not old:
            return
        
        with self.repository.engine.begin() as conn:
            query = update(Device).where(Device.id == device.id).values(
                name = device.name or old.name,
                type = device.type or old.type,
                ip = device.ip or old.ip,
                user_id = device.user_id or old.user_id
            )
            conn.execute(query)
    
    def delete_device(self, id):
        with self.repository.engine.begin() as conn:
            # DELETE * FROM DEVICE WHERE Device.ID = ID
            query = delete(Device).where(Device.id == id)
            conn.execute(query)
