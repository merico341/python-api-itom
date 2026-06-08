from enum import Enum
from functools import wraps
from datetime import datetime
from flask import abort, request
from flask_login import current_user
from model.log import Log
from service.log_service import LogService
from util.log_enum_util import LogOperation, LogStatus

class UserRole(Enum):
    USER = "USER"
    TI = "TI"
    ADM = "ADM"


def roles_required(*roles: UserRole):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            log_service = LogService()
            
            rota_acessada = request.path

            if not current_user.is_authenticated:
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=f"Tentativa de acesso anônimo bloqueada na rota: {rota_acessada}",
                    device_id=None,
                    user_id=3,
                    date_hour=datetime.now()
                ))
                abort(401, description="Não autenticado. Por favor, faça login para acessar este recurso.")
                        
            try:
                role_atual_usuario = current_user.role
                if isinstance(role_atual_usuario, Enum):
                    user_role_enum = role_atual_usuario
                else:
                    user_role_enum = UserRole[str(role_atual_usuario).upper()]
            except (KeyError, AttributeError):
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=f"Usuário {current_user.name} (ID: {current_user.id}) possui um cargo inválido no banco de dados.",
                    device_id=None,
                    user_id=current_user.id,
                    date_hour=datetime.now()
                ))
                abort(403, description="Acesso negado. Seu nível de acesso não foi reconhecido pelo sistema.")
            
            if user_role_enum not in roles:
                permissoes_necessarias = [r.value for r in roles]
                motivo_bloqueio = f"Acesso negado para o perfil {user_role_enum.value} na rota {rota_acessada}. Essa operação exige: {permissoes_necessarias}"
                
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=motivo_bloqueio,
                    device_id=None,
                    user_id=current_user.id,
                    date_hour=datetime.now()
                ))
                
                abort(403, description=f"Acesso negado. Esta operação exige um dos seguintes perfis: {permissoes_necessarias}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator