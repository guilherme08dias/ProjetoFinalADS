# 🎯 PROMPT PARA GOOGLE ANTIGRAVITY - ETAPA 3 DO DENTALSYSTEM

## 📌 CONTEXTO DO PROJETO

Este é o **Projeto Integrador DentalSystem** - Um sistema web de agendamento para consultórios odontológicos desenvolvido em Flask + PostgreSQL.

**Etapas Completadas:**
- ✅ Etapa 1: Arquitetura MVC, Login básico, Dashboard
- ✅ Etapa 2: Banco de dados, Models SQLAlchemy, Integração PostgreSQL

**Etapa Atual:** 3 - Melhorias de Segurança + CRUD completo de Agendamentos

---

## 🔐 OBJETIVO PRINCIPAL DA ETAPA 3

**Transformar o MVP funcional em um sistema seguro e completo, implementando:**
1. ✅ Autenticação segura com hashing de senhas
2. ✅ Controle de sessão e autorização
3. ✅ Proteção CSRF
4. ✅ CRUD completo de agendamentos
5. ✅ Validação de dados
6. ✅ Tratamento de erros robusto

---

## 📁 ESTRUTURA ATUAL DO PROJETO

```
dentalsystem/
├── app.py
├── models.py
├── requirements.txt
└── templates/
    ├── base.html
    ├── login.html
    └── index.html
```

---

## ⚠️ PROBLEMAS CRÍTICOS A RESOLVER

### 🔴 CRÍTICO #1: Senhas em Texto Plano
**Problema:** `user.senha == senha` - Senhas armazenadas sem criptografia
**Solução:** Usar `werkzeug.security` com `generate_password_hash()` e `check_password_hash()`

### 🔴 CRÍTICO #2: Sem Controle de Sessão
**Problema:** Não há controle de usuário logado - qualquer pessoa acessa qualquer rota
**Solução:** Implementar `Flask-Login` com `@login_required` decorator

### 🔴 CRÍTICO #3: Credenciais Hardcoded
**Problema:** `postgresql://postgres:1234@localhost:5432/dentalsystem` exposta no código
**Solução:** Usar arquivo `.env` com `python-dotenv`

### 🔴 CRÍTICO #4: Sem Proteção CSRF
**Problema:** Formulários sem proteção contra ataques CSRF
**Solução:** Implementar `Flask-WTF` com tokens CSRF

### 🟡 IMPORTANTE #5: CRUD Incompleto
**Problema:** Só há listagem de agendamentos, faltam Create, Update, Delete
**Solução:** Implementar todas as operações CRUD com validações

---

## 📊 CÓDIGO ATUAL (BASE PARA MELHORIAS)

### models.py (Atual)
```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    id = db.Column(db.Integer, primary_key=True)
    paciente_nome = db.Column(db.String(100), nullable=False)
    servico_tipo = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pendente')
```

### app.py (Atual)
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        user = Usuario.query.filter_by(email=email).first()
        if user and user.senha == senha:  # ❌ INSEGURO!
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="Email ou senha inválidos")
    return render_template('login.html')
```

---

## 🚀 INSTRUÇÕES PARA O ANTIGRAVITY

### PASSO 1: Criar arquivo `.env`

```
DATABASE_URL=postgresql://postgres:1234@localhost:5432/dentalsystem
SECRET_KEY=sua-chave-secreta-super-segura-aqui-32-caracteres
DEBUG=True
FLASK_ENV=development
```

**IMPORTANTE:** Adicionar `.env` ao `.gitignore`

---

### PASSO 2: Atualizar `requirements.txt`

Substituir todo o conteúdo por:

```
Flask==3.0.0
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.1
Flask-Login==0.6.2
Flask-WTF==1.2.1
WTForms==3.1.1
email-validator==2.1.0
pytest==7.4.3
pytest-flask==1.3.0
```

---

### PASSO 3: Refatorar `models.py`

**OBJETIVO:** Adicionar segurança, relacionamentos e timestamps

```python
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    senha = db.Column(db.String(255), nullable=False)  # Hash seguro
    tipo = db.Column(db.String(20), default='paciente')  # paciente ou admin
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamento com agendamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Criptografa a senha com Werkzeug"""
        if len(password) < 8:
            raise ValueError("Senha deve ter no mínimo 8 caracteres")
        self.senha = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha, password)
    
    def is_admin(self):
        """Verifica se é administrador"""
        return self.tipo == 'admin'
    
    def to_dict(self):
        """Converte para dicionário (útil para APIs)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo': self.tipo
        }


class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    dentista_responsavel = db.Column(db.String(100), nullable=True)
    servico_tipo = db.Column(db.String(100), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='pendente', index=True)
    observacoes = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints para evitar conflitos
    __table_args__ = (
        db.UniqueConstraint('dentista_responsavel', 'data_hora', name='uq_dentista_horario'),
        db.CheckConstraint("status IN ('pendente', 'confirmado', 'cancelado', 'realizado')", name='check_status'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'paciente_nome': self.paciente.nome,
            'dentista_responsavel': self.dentista_responsavel,
            'servico_tipo': self.servico_tipo,
            'data_hora': self.data_hora.isoformat(),
            'status': self.status,
            'observacoes': self.observacoes,
            'data_criacao': self.data_criacao.isoformat()
        }
```

---

### PASSO 4: Refatorar `app.py` com Segurança

```python
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from datetime import datetime

from models import db, Usuario, Agendamento

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# ========== CONFIGURAÇÃO ==========
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
app.config['WTF_CSRF_ENABLED'] = True

# Inicializar extensões
db.init_app(app)
csrf = CSRFProtect(app)

# Configurar Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para continuar.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Cadastro de novo usuário (paciente)"""
    if request.method == 'POST':
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        confirma_senha = request.form.get('confirma_senha')
        
        # Validações
        if not nome or not email or not senha:
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('register'))
        
        if len(senha) < 8:
            flash('Senha deve ter no mínimo 8 caracteres', 'error')
            return redirect(url_for('register'))
        
        if senha != confirma_senha:
            flash('As senhas não coincidem', 'error')
            return redirect(url_for('register'))
        
        if Usuario.query.filter_by(email=email).first():
            flash('Email já cadastrado', 'error')
            return redirect(url_for('register'))
        
        # Criar novo usuário
        novo_usuario = Usuario(nome=nome, email=email, tipo='paciente')
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuário com autenticação segura"""
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        
        # Validação
        if not email or not senha:
            flash('Email e senha são obrigatórios', 'error')
            return render_template('login.html')
        
        # Buscar usuário
        usuario = Usuario.query.filter_by(email=email).first()
        
        # Verificar credenciais SEGURAMENTE
        if usuario and usuario.check_password(senha):
            if not usuario.ativo:
                flash('Usuário inativo. Entre em contato com o administrador.', 'error')
                return render_template('login.html')
            
            login_user(usuario, remember=True)  # remember=True para "lembrar de mim"
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            
            # Redirecionar para admin ou dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos', 'error')
            return render_template('login.html')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout de usuário"""
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))


# ========== ROTAS PRINCIPAIS ==========

@app.route('/')
@login_required
def index():
    """Dashboard principal com agendamentos"""
    try:
        agendamentos = Agendamento.query.all()
        total_agendamentos = len(agendamentos)
        pendentes = len([a for a in agendamentos if a.status == 'pendente'])
        confirmados = len([a for a in agendamentos if a.status == 'confirmado'])
        
        return render_template('index.html', 
                             agendamentos=agendamentos,
                             total_agendamentos=total_agendamentos,
                             pendentes=pendentes,
                             confirmados=confirmados)
    except Exception as e:
        flash(f'Erro ao carregar agendamentos: {str(e)}', 'error')
        return render_template('index.html', agendamentos=[], total_agendamentos=0, pendentes=0, confirmados=0)


# ========== ROTAS DE AGENDAMENTOS (CRUD) ==========

@app.route('/agendamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_agendamento():
    """Criar novo agendamento"""
    if request.method == 'POST':
        paciente_nome = request.form.get('paciente_nome')
        dentista_responsavel = request.form.get('dentista_responsavel')
        servico_tipo = request.form.get('servico_tipo')
        data_hora_str = request.form.get('data_hora')
        observacoes = request.form.get('observacoes', '')
        
        # Validações
        if not all([paciente_nome, dentista_responsavel, servico_tipo, data_hora_str]):
            flash('Todos os campos são obrigatórios', 'error')
            return redirect(url_for('novo_agendamento'))
        
        try:
            data_hora = datetime.fromisoformat(data_hora_str)
            
            # Verificar conflito de horário
            conflito = Agendamento.query.filter(
                Agendamento.dentista_responsavel == dentista_responsavel,
                Agendamento.data_hora == data_hora,
                Agendamento.status != 'cancelado'
            ).first()
            
            if conflito:
                flash('Já existe um agendamento neste horário para este dentista', 'error')
                return redirect(url_for('novo_agendamento'))
            
            # Criar agendamento
            agendamento = Agendamento(
                paciente_id=current_user.id,
                paciente_nome=paciente_nome,
                dentista_responsavel=dentista_responsavel,
                servico_tipo=servico_tipo,
                data_hora=data_hora,
                observacoes=observacoes,
                status='pendente'
            )
            
            db.session.add(agendamento)
            db.session.commit()
            
            flash('Agendamento criado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        except ValueError:
            flash('Formato de data/hora inválido', 'error')
            return redirect(url_for('novo_agendamento'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar agendamento: {str(e)}', 'error')
            return redirect(url_for('novo_agendamento'))
    
    return render_template('novo_agendamento.html')


@app.route('/agendamentos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_agendamento(id):
    """Editar agendamento existente"""
    agendamento = Agendamento.query.get(id)
    
    if not agendamento:
        flash('Agendamento não encontrado', 'error')
        return redirect(url_for('index'))
    
    # Verificar permissão (admin ou dono)
    if not current_user.is_admin() and agendamento.paciente_id != current_user.id:
        flash('Sem permissão para editar este agendamento', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        try:
            agendamento.paciente_nome = request.form.get('paciente_nome')
            agendamento.dentista_responsavel = request.form.get('dentista_responsavel')
            agendamento.servico_tipo = request.form.get('servico_tipo')
            agendamento.status = request.form.get('status')
            agendamento.observacoes = request.form.get('observacoes', '')
            
            data_hora_str = request.form.get('data_hora')
            if data_hora_str:
                agendamento.data_hora = datetime.fromisoformat(data_hora_str)
            
            db.session.commit()
            flash('Agendamento atualizado com sucesso!', 'success')
            return redirect(url_for('index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar: {str(e)}', 'error')
            return redirect(url_for('editar_agendamento', id=id))
    
    return render_template('editar_agendamento.html', agendamento=agendamento)


@app.route('/agendamentos/<int:id>/deletar', methods=['POST'])
@login_required
def deletar_agendamento(id):
    """Deletar agendamento"""
    agendamento = Agendamento.query.get(id)
    
    if not agendamento:
        flash('Agendamento não encontrado', 'error')
        return redirect(url_for('index'))
    
    # Verificar permissão
    if not current_user.is_admin() and agendamento.paciente_id != current_user.id:
        flash('Sem permissão para deletar este agendamento', 'error')
        return redirect(url_for('index'))
    
    try:
        db.session.delete(agendamento)
        db.session.commit()
        flash('Agendamento deletado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar: {str(e)}', 'error')
    
    return redirect(url_for('index'))


# ========== TESTES DE BANCO DE DADOS ==========

@app.route('/test-db')
def test_db():
    """Teste de conexão com banco (REMOVER EM PRODUÇÃO)"""
    try:
        usuarios = Usuario.query.all()
        return jsonify({
            'status': 'ok',
            'total_usuarios': len(usuarios),
            'mensagem': 'Conexão com banco funcionando!'
        })
    except Exception as e:
        return jsonify({'status': 'erro', 'mensagem': str(e)}), 500


# ========== TRATAMENTO DE ERROS ==========

@app.errorhandler(404)
def pagina_nao_encontrada(error):
    return render_template('erro.html', codigo=404, mensagem='Página não encontrada'), 404

@app.errorhandler(500)
def erro_servidor(error):
    db.session.rollback()
    return render_template('erro.html', codigo=500, mensagem='Erro interno do servidor'), 500

@app.errorhandler(403)
def acesso_negado(error):
    return render_template('erro.html', codigo=403, mensagem='Acesso negado'), 403


# ========== INICIALIZAÇÃO ==========

if __name__ == '__main__':
    with app.app_context():
        try:
            # Criar tabelas
            db.create_all()
            print("✅ Banco de dados conectado e tabelas verificadas!")
            
            # Criar usuário admin padrão (se não existir)
            if not Usuario.query.filter_by(email='admin@dentalsystem.com').first():
                admin = Usuario(
                    nome='Administrador',
                    email='admin@dentalsystem.com',
                    tipo='admin',
                    ativo=True
                )
                admin.set_password('admin123')  # MUDE ISSO EM PRODUÇÃO!
                db.session.add(admin)
                db.session.commit()
                print("✅ Usuário admin criado: admin@dentalsystem.com / admin123")
            
        except Exception as e:
            print(f"❌ ERRO AO CONECTAR NO BANCO: {e}")
    
    app.run(debug=True)
```

---

### PASSO 5: Criar templates HTML com Proteção CSRF

#### `login.html` (Atualizado)
```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h3 class="mb-0">🔐 Login</h3>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST" novalidate>
                        {{ csrf_token() }}
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="password" class="form-label">Senha</label>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                        
                        <button type="submit" class="btn btn-primary w-100">Entrar</button>
                    </form>
                    
                    <hr>
                    <p class="text-center">Não tem cadastro? <a href="{{ url_for('register') }}">Cadastre-se aqui</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### `register.html` (Novo)
```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-5">
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card shadow">
                <div class="card-header bg-success text-white">
                    <h3 class="mb-0">📝 Cadastro</h3>
                </div>
                <div class="card-body">
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show" role="alert">
                                    {{ message }}
                                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                                </div>
                            {% endfor %}
                        {% endif %}
                    {% endwith %}
                    
                    <form method="POST" novalidate>
                        {{ csrf_token() }}
                        
                        <div class="mb-3">
                            <label for="nome" class="form-label">Nome Completo</label>
                            <input type="text" class="form-control" id="nome" name="nome" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="email" class="form-label">Email</label>
                            <input type="email" class="form-control" id="email" name="email" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="senha" class="form-label">Senha (mínimo 8 caracteres)</label>
                            <input type="password" class="form-control" id="senha" name="senha" minlength="8" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="confirma_senha" class="form-label">Confirmar Senha</label>
                            <input type="password" class="form-control" id="confirma_senha" name="confirma_senha" minlength="8" required>
                        </div>
                        
                        <button type="submit" class="btn btn-success w-100">Cadastrar</button>
                    </form>
                    
                    <hr>
                    <p class="text-center">Já tem cadastro? <a href="{{ url_for('login') }}">Faça login aqui</a></p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### `novo_agendamento.html` (Novo)
```html
{% extends "base.html" %}

{% block content %}
<div class="container mt-4">
    <h1>📅 Novo Agendamento</h1>
    
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                    {{ message }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <div class="row mt-4">
        <div class="col-md-8">
            <div class="card">
                <div class="card-body">
                    <form method="POST" novalidate>
                        {{ csrf_token() }}
                        
                        <div class="mb-3">
                            <label for="paciente_nome" class="form-label">Nome do Paciente</label>
                            <input type="text" class="form-control" id="paciente_nome" name="paciente_nome" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="dentista_responsavel" class="form-label">Dentista Responsável</label>
                            <input type="text" class="form-control" id="dentista_responsavel" name="dentista_responsavel" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="servico_tipo" class="form-label">Tipo de Serviço</label>
                            <select class="form-control" id="servico_tipo" name="servico_tipo" required>
                                <option value="">Selecione...</option>
                                <option value="Consulta">Consulta</option>
                                <option value="Limpeza">Limpeza</option>
                                <option value="Restauração">Restauração</option>
                                <option value="Extração">Extração</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="data_hora" class="form-label">Data e Hora</label>
                            <input type="datetime-local" class="form-control" id="data_hora" name="data_hora" required>
                        </div>
                        
                        <div class="mb-3">
                            <label for="observacoes" class="form-label">Observações</label>
                            <textarea class="form-control" id="observacoes" name="observacoes" rows="4"></textarea>
                        </div>
                        
                        <button type="submit" class="btn btn-success">Agendar</button>
                        <a href="{{ url_for('index') }}" class="btn btn-secondary">Cancelar</a>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

Para o Antigravity seguir esta ordem:

1. **Atualizar `requirements.txt`**
   - ✅ Adicionar todas as dependências

2. **Criar arquivo `.env`**
   - ✅ Com variáveis de ambiente

3. **Refatorar `models.py`**
   - ✅ Adicionar hashing de senhas
   - ✅ Adicionar UserMixin
   - ✅ Adicionar relacionamentos
   - ✅ Adicionar timestamps

4. **Refatorar `app.py`**
   - ✅ Implementar Flask-Login
   - ✅ Implementar CSRF protection
   - ✅ Usar variáveis de ambiente
   - ✅ Criar rotas de cadastro
   - ✅ Implementar CRUD de agendamentos
   - ✅ Adicionar validações

5. **Atualizar templates**
   - ✅ Adicionar {{ csrf_token() }} em forms
   - ✅ Criar register.html
   - ✅ Criar novo_agendamento.html
   - ✅ Criar editar_agendamento.html
   - ✅ Criar erro.html
   - ✅ Atualizar base.html com logout

6. **Testes Básicos**
   - ✅ Testar login com usuário admin
   - ✅ Testar cadastro de novo usuário
   - ✅ Testar criação de agendamento
   - ✅ Testar edição de agendamento
   - ✅ Testar exclusão de agendamento

---

## 📝 NOTAS IMPORTANTES

- **Senha Padrão do Admin:** `admin123` - MUDE EM PRODUÇÃO
- **SECRET_KEY:** Gere uma chave aleatória segura em produção
- **DATABASE_URL:** Certifique-se que o PostgreSQL está rodando
- **CSRF Protection:** Essencial para segurança, não remova
- **Login Required:** Usar `@login_required` em todas rotas protegidas

---

## 🎯 RESULTADO ESPERADO

Após esta etapa, o sistema terá:

✅ **Segurança robusta** (senhas hasheadas, CSRF, sessões)  
✅ **CRUD completo** de agendamentos (Create, Read, Update, Delete)  
✅ **Validações de dados** (email, datas, conflitos)  
✅ **Controle de acesso** (admin vs paciente)  
✅ **Tratamento de erros** adequado  
✅ **Pronto para próximas etapas** (API REST, Notificações)

---

**Status:** Pronto para Antigravity executar! ✅
