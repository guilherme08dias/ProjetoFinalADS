# Histórico de Desenvolvimento - DentalSystem

Este documento registra o progresso do Projeto Integrador, detalhando as decisões técnicas e implementações realizadas pela equipe em cada fase do cronograma.

---

## ✅ ETAPA 1: Planejamento e Arquitetura (MVP)
**Status:** Concluído
**Foco:** Estruturação do ambiente e Interface do Usuário (UI).

### Atividades Realizadas:
1.  **Definição de Arquitetura:**
    *   Adotado o padrão **MVC (Model-View-Controller)** para separar lógica de negócio e interface.
    *   **Stack Definida:** Python (Flask) para o Backend e Bootstrap 5 para o Frontend.
2.  **Desenvolvimento Frontend (Views):**
    *   Criação de templates HTML responsivos (`base.html`, `login.html`, `index.html`).
    *   Implementação de layout administrativo com Sidebar (Menu Lateral) e Cards de KPI, fugindo do modelo de "site institucional".
3.  **Configuração do Ambiente:**
    *   Estruturação de pastas padrão do Flask.
    *   Criação do arquivo de requisitos (`requirements.txt`).

---

## ✅ ETAPA 2: Banco de Dados e Backend (Funcionalidades Básicas)
**Status:** Concluído
**Foco:** Persistência de dados e Autenticação.

### Atividades Realizadas:
1.  **Implementação do Banco de Dados:**
    *   SGBD Escolhido: **PostgreSQL**.
    *   Biblioteca de ORM: **SQLAlchemy**. Isso permitiu a criação das tabelas via código Python (`models.py`), sem necessidade de scripts SQL manuais complexos.
2.  **Integração Backend (Controller):**
    *   Configuração da string de conexão no `app.py`.
    *   Implementação da lógica de criação automática de tabelas (`db.create_all()`).
    *   Criação de rotas conectadas ao banco: O Login agora valida credenciais reais e o Dashboard busca agendamentos na tabela.
3.  **Segurança e Testes:**
    *   Implementação de "Data Seeding": O sistema verifica se existe um admin e cria um padrão (`admin@dentalsystem.com`) automaticamente para facilitar os testes iniciais.

---

## 📅 PRÓXIMOS PASSOS: ETAPA 3 (Funcionalidades Complementares)
**Objetivo:** Implementar o CRUD completo de Agendamentos.
*   Criar formulário de "Novo Agendamento" (Insert).
*   Permitir edição de status e exclusão de consultas (Update/Delete).
*   Melhorar validações de formulário.
