from enum import Enum
from functools import wraps
from flask import abort
from flask_login import current_user

class UserRole(Enum):
    USER = "USER"   # Usuário comum / Solicitante de chamados
    TI = "TI"       # Técnico / Analista de TI (Gerencia incidentes e redes)
    ADM = "ADM"     # Administrador do Sistema (Acesso total e exclusões)


def roles_required(*roles: UserRole):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401, description="Não autenticado. Por favor, faça login para acessar este recurso.")
            
            try:
                user_role_enum = UserRole[current_user.role.upper()]
            except (KeyError, AttributeError):
                abort(403, description="Acesso negado. Seu nível de acesso não foi reconhecido pelo sistema.")
            
            if user_role_enum not in roles:
                permissoes_necessarias = [r.value for r in roles]
                abort(403, description=f"Acesso negado. Esta operação exige um dos seguintes perfis: {permissoes_necessarias}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator