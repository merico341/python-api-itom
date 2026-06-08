from sqlalchemy import delete, insert, select, update

import os
from model.device import Device
from repository.repository import Repository
from service.log_service import LogService, Log
from util.log_enum_util import LogOperation, LogStatus
import requests

class DeviceService():

    def __init__(self):
        self.repository = Repository()
        self.log_service = LogService()

        self.sn_instance = os.getenv("SERVICENOW_INSTANCE_URL", "https://dev328829.service-now.com/")
        self.sn_user = os.getenv("SERVICENOW_USER", "admin")
        self.sn_password = os.getenv("SERVICENOW_PASSWORD", "/lg0@wCIZo9J")


    def create_device(self, device: Device):
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
            operation=LogOperation.CREATE,
            status=LogStatus.SUCCESS,
            description=f"Dispositivo '{device.name}' (ID: {device.id}) cadastrado com sucesso.",
            device_id=device.id
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

    def sync_servicenow_devices(self, user_id_executante, class_name=None):
        """
        Consome a API de Instância do CMDB do ServiceNow de forma dinâmica
        com base no className enviado por JSON e executa apenas a inserção (INSERT)
        dos ativos usando a função create_device local.
        """
        import requests

        # Define um valor padrão caso o front-end não envie um className específico
        if not class_name:
            class_name = "cmdb_ci_hardware"
        
        # Montagem dinâmica da URL com a classe solicitada pelo JSON
        url = f"{self.sn_instance}/api/now/cmdb/instance/{class_name}"
        
        params = {
            "sysparm_query": "ip_addressISNOTEMPTY",
            "sysparm_fields": "name,sys_class_name,ip_address",
            "sysparm_limit": "50"
        }

        try:
            # 1. Consome a API do ServiceNow
            response = requests.get(
                url, 
                auth=(self.sn_user, self.sn_password), 
                params=params,
                headers={"Accept": "application/json"},
                timeout=15
            )

            if response.status_code != 200:
                # Captura o texto exato do erro que o ServiceNow devolveu
                detalhe_erro = response.text
                print(f"[ERRO SERVICENOW] Resposta do Servidor: {detalhe_erro}")
                raise Exception(f"Erro na CMDB API do ServiceNow: Status {response.status_code} - {detalhe_erro}")

            records = response.json().get("result", [])
            inserted_count = 0

            # 2. Varre os registros trazidos e executa estritamente o INSERT
            for rec in records:
                name = rec.get("name", "Dispositivo Sem Nome")
                ip = rec.get("ip_address")
                device_type = rec.get("sys_class_name", class_name)

                # Instancia o modelo e chama o seu método local que lida com o INSERT e Logs
                novo_device = Device(
                    name=name,
                    type=device_type,
                    ip=ip,
                    user_id=user_id_executante
                )
                
                self.create_device(novo_device)
                inserted_count += 1

            # 3. Registro de Log Geral de SUCESSO da Operação de Carga/Sincronismo
            self.log_service.create_log(Log(
                operation=LogOperation.CONNECT,
                status=LogStatus.SUCCESS,
                description=f"Carga CMDB da classe '{class_name}' concluída. Total de inserções: {inserted_count}.",
                user_id=user_id_executante
            ))

            return {
                "message": f"Sincronização da classe {class_name} realizada com sucesso", 
                "inserted": inserted_count,
                "updated": 0
            }

        except Exception as e:
            # 4. Registro de Log Geral de FALHA
            self.log_service.create_log(Log(
                operation=LogOperation.CONNECT,
                status=LogStatus.FAILED,
                description=f"Falha ao processar carga da instância CMDB da classe '{class_name}': {str(e)}",
                user_id=user_id_executante
            ))
            raise e

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
            operation=LogOperation.UPDATE,
            status=LogStatus.SUCCESS,
            description=f"Dispositivo ID {device.id} atualizado.",
            device_id=device.id
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
            operation=LogOperation.DELETE,
            status=LogStatus.SUCCESS,
            description=f"Dispositivo '{old.name}' (ID: {id}) foi removido permanentemente.",
            device_id=old.id
        ))