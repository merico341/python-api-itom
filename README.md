# 🚀 API ITOM - Gerenciamento de Infraestrutura e Incidentes

Uma API RESTful robusta desenvolvida em Python para gerenciar a infraestrutura de TI (ITOM) e o atendimento a serviços (ITSM). O sistema permite o rastreamento de dispositivos (CIs), mapeamento de conexões de rede, gestão de usuários e abertura de incidentes, tudo com trilha de auditoria (Logs) automatizada.

## 🌐 Acesse o Projeto

- **Front-end (Interface Visual):** [Projeto Resolve IT - Vercel](https://projetoresolveit.vercel.app/)
- **Back-end (API e Swagger):** [Documentação da API - Render](https://python-api-itom.onrender.com/docs)

## 📋 Funcionalidades

- **Gestão de Usuários (Auth/Users):** Cadastro, listagem, deleção e autenticação de usuários e administradores.
- **Gestão de Dispositivos (Devices):** Inventário de infraestrutura, registrando nome, tipo, IP e o usuário responsável.
- **Mapeamento de Rede (Connections):** Criação de vínculos e topologia entre dispositivos (Origem e Destino).
- **Gestão de Incidentes (Incidents):** Abertura de chamados vinculados a usuários (`caller_id`) e dispositivos, com controle de estado (`state`) e prioridade (`priority`).
- **Auditoria de Sistema (Logs):** Registro automático de operações sensíveis (CREATE, UPDATE, DELETE, LOGIN) no banco de dados.

## 🛠️ Arquitetura do Projeto

O projeto segue o padrão de camadas (Layered Architecture) para garantir escalabilidade, manutenção e separação de responsabilidades:

- `controller/`: É a porta de entrada da API. Define as rotas (endpoints), a documentação interativa (Swagger) e recebe as requisições HTTP usando Flask-RESTX.
- `service/`: É o cérebro do projeto. Contém as regras de negócio, validações lógicas e a orquestração do que deve acontecer antes de salvar ou deletar algo.
- `repository/`: Camada exclusiva para gerenciar a conexão com o banco de dados (padrão Singleton) e a engine do SQLAlchemy.
- `model/`: Mapeamento das entidades do banco de dados (Tabelas, Colunas, Relacionamentos e Chaves Estrangeiras) utilizando o SQLAlchemy (DeclarativeBase).
- `util/`: É como a caixa de ferramentas do sistema. Contém utilitários globais, como os **Enums** de status e prioridades, garantindo que o sistema inteiro utilize nomenclaturas e estados padronizados sem duplicação de código.