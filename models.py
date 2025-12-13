# ============================================
# Modelos do Banco de Dados - DentalSystem
# Projeto Integrador - Equipe de Desenvolvimento
# ============================================
# Este arquivo define as entidades do sistema conforme
# o Diagrama Entidade-Relacionamento (MER) do projeto.
# ============================================

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ============================================
# MODELO: Usuario
# ============================================
# Representa todos os usuários do sistema (pacientes e administradores).
# Implementa UserMixin para integração com Flask-Login.
# ============================================
class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(256), nullable=False)
    
    # Perfil: 'admin' para administradores, 'paciente' para pacientes
    perfil = db.Column(db.String(20), nullable=False, default='paciente')
    
    # Dados adicionais do paciente
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True)
    
    # Controle de registro
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy=True, foreign_keys='Agendamento.paciente_id')
    
    # Métodos para gerenciamento de senha (segurança)
    def set_password(self, senha):
        """Cria hash da senha para armazenamento seguro"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_password(self, senha):
        """Verifica se a senha fornecida corresponde ao hash"""
        return check_password_hash(self.senha_hash, senha)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.perfil == 'admin'
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'


# ============================================
# MODELO: Servico
# ============================================
# Representa os serviços/tratamentos oferecidos pelo consultório.
# Cada serviço tem duração e preço definidos.
# ============================================
class Servico(db.Model):
    __tablename__ = 'servicos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    duracao_minutos = db.Column(db.Integer, nullable=False, default=30)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Controle de disponibilidade
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='servico', lazy=True)
    
    def __repr__(self):
        return f'<Servico {self.nome}>'


# ============================================
# MODELO: Dentista
# ============================================
# Representa os dentistas do consultório.
# Pode estar vinculado a um usuário do sistema para login próprio.
# ============================================
class Dentista(db.Model):
    __tablename__ = 'dentistas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cro = db.Column(db.String(20), unique=True, nullable=False)  # Registro no Conselho Regional
    especialidade = db.Column(db.String(100))
    
    # Vinculação opcional com usuário do sistema
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # Controle de disponibilidade
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    usuario = db.relationship('Usuario', backref='dentista_perfil', uselist=False)
    agendamentos = db.relationship('Agendamento', backref='dentista', lazy=True)
    
    def __repr__(self):
        return f'<Dentista {self.nome} - CRO: {self.cro}>'


# ============================================
# MODELO: Agendamento
# ============================================
# Representa as consultas agendadas no sistema.
# Conecta paciente, dentista e serviço com data/hora.
# ============================================
class Agendamento(db.Model):
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Data e hora do agendamento
    data_hora_inicio = db.Column(db.DateTime, nullable=False)
    data_hora_fim = db.Column(db.DateTime, nullable=False)
    
    # Status: 'pendente', 'confirmado', 'cancelado', 'concluido'
    status = db.Column(db.String(20), default='pendente')
    
    # Observações adicionais do paciente ou dentista
    observacoes = db.Column(db.Text)
    
    # Chaves estrangeiras (relacionamentos)
    paciente_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    dentista_id = db.Column(db.Integer, db.ForeignKey('dentistas.id'), nullable=False)
    servico_id = db.Column(db.Integer, db.ForeignKey('servicos.id'), nullable=False)
    
    # Controle de registro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Agendamento {self.id} - {self.data_hora_inicio}>'
    
    def get_status_badge(self):
        """Retorna a classe CSS para o badge de status"""
        badges = {
            'pendente': 'warning',
            'confirmado': 'success',
            'cancelado': 'danger',
            'concluido': 'info'
        }
        return badges.get(self.status, 'secondary')


# ============================================
# MODELO: Configuracao
# ============================================
# Armazena configurações gerais da clínica.
# Deve existir apenas um registro nesta tabela.
# ============================================
class Configuracao(db.Model):
    __tablename__ = 'configuracoes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Dados da clínica
    nome_clinica = db.Column(db.String(200), default='DentalSystem')
    telefone_clinica = db.Column(db.String(20))
    endereco_clinica = db.Column(db.String(300))
    
    # Horários de funcionamento - TURNO MANHÃ
    hora_inicio_manha = db.Column(db.String(5), default='08:00')
    hora_fim_manha = db.Column(db.String(5), default='12:00')
    
    # Horários de funcionamento - TURNO TARDE
    hora_inicio_tarde = db.Column(db.String(5), default='14:00')
    hora_fim_tarde = db.Column(db.String(5), default='18:00')
    
    intervalo_consultas = db.Column(db.Integer, default=30)  # Minutos
    
    # Dias da semana (1=Segunda, 7=Domingo)
    segunda = db.Column(db.Boolean, default=True)
    terca = db.Column(db.Boolean, default=True)
    quarta = db.Column(db.Boolean, default=True)
    quinta = db.Column(db.Boolean, default=True)
    sexta = db.Column(db.Boolean, default=True)
    sabado = db.Column(db.Boolean, default=False)
    domingo = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Configuracao {self.nome_clinica}>'
