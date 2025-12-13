# DentalSystem

Sistema de Agendamento Online para Consultórios Odontológicos

## Projeto Integrador - 4º Semestre
**Curso:** Análise e Desenvolvimento de Sistemas  
**Alunos:** Denilson Garda, Guilherme Dias, Jessica Zamberlan

---

## Tecnologias Utilizadas

- **Backend:** Python 3.11, Flask 3.0
- **Banco de Dados:** PostgreSQL / SQLite
- **ORM:** SQLAlchemy 2.0
- **Autenticação:** Flask-Login
- **Segurança:** Flask-WTF (CSRF), Werkzeug (hash de senhas)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap Icons

---

## Como Executar

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente
```bash
copy .env.example .env
```
Edite o arquivo `.env` com suas credenciais.

### 3. Executar a Aplicação
```bash
python app.py
```

### 4. Acessar o Sistema
Abra o navegador em: http://127.0.0.1:5000

**Credenciais de Teste:**
- Email: admin@dentalsystem.com
- Senha: admin123

---

## Estrutura do Projeto

```
DentalSystem/
├── app.py              # Aplicação principal Flask
├── models.py           # Modelos do banco de dados
├── requirements.txt    # Dependências
├── wsgi.py             # Arquivo para produção (Gunicorn)
├── .env                # Variáveis de ambiente
├── static/css/         # Estilos customizados
├── templates/          # Templates HTML
│   ├── admin/          # Templates do administrador
│   └── paciente/       # Templates do paciente
└── prints/             # Capturas de tela do sistema
```

---

## Funcionalidades

### Área Administrativa
- Dashboard com estatísticas e filtro por período
- Relatório de receita (agendamentos concluídos)
- Gerenciamento de Pacientes (CRUD)
- Gerenciamento de Serviços (CRUD)
- Gerenciamento de Dentistas (CRUD)
- Agenda de Consultas com verificação de conflitos
- Configurações da Clínica (horários de funcionamento)

### Área do Paciente
- Login e Cadastro
- Visualização de Agendamentos
- Novo Agendamento com horários disponíveis
- Cancelamento de consultas

---

## Licença
Projeto acadêmico desenvolvido para fins educacionais.
