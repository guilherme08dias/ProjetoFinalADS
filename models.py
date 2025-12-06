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