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