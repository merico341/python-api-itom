from sqlalchemy import delete, insert, select, update

from model.user import User
from repository.repository import Repository

class UserService():

    def __init__(self):
        self.repository = Repository()

    def create_user(self, user: User):
        with self.repository.engine.begin() as conn:
            # INSERT INTO USER (nome, email, departament) VALUES (user.id, user.nome, user.email)
            query = insert(User).values(
                name = user.name,
                email = user.email,
                departament = user.departament
            )
            conn.execute(query)

    def list_users(self):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM USER
            query = select(User)
            result = conn.execute(query)
            return [User(**row) for row in result.mappings()]

    def select_user(self, id):
        with self.repository.engine.connect() as conn:
            # SELECT * FROM USER WHERE USER.ID = id 
            query = select(User).where(User.id == id)
            result = conn.execute(query)
            row = result.mappings().first()

            return User(**row) if row else None

    def update_user(self, user: User):
        old = self.select_user(user.id)

        if not old:
            return

        with self.repository.engine.begin() as conn:
            # UPDATE * FROM USER WHERE USER.ID = id 
            query = update(User).where(User.id == user.id).values(
                name = user.name or old.name,
                email = user.email or old.email,
                departament = user.departament or old.departament
            )
            conn.execute(query)

    def delete_user(self, id):
        with self.repository.engine.begin() as conn:
            # DELETE * FROM USER WHERE USER.ID = id
            query = delete(User).where(User.id == id)
            conn.execute(query)
