# ============================================
# Aplicação Principal - DentalSystem
# Projeto Integrador - Equipe de Desenvolvimento
# ============================================
# Sistema de Agendamento Online para Consultório Odontológico
# Este arquivo contém todas as rotas e lógica da aplicação.
# ============================================

import os
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from models import db, Usuario, Servico, Dentista, Agendamento, Configuracao

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


# ============================================
# CONFIGURAÇÃO DA APLICAÇÃO
# ============================================
app = Flask(__name__, template_folder='templates')

# Configurações de segurança
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'chave-padrao-desenvolvimento')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/dentalsystem')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializa extensões
db.init_app(app)
csrf = CSRFProtect(app)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Carrega usuário pelo ID para o Flask-Login"""
    return Usuario.query.get(int(user_id))


@app.context_processor
def inject_config():
    """Injeta as configurações da clínica em todos os templates"""
    config = Configuracao.query.first()
    if not config:
        config = Configuracao()
    return {'config_clinica': config}


# ============================================
# DECORADOR: Verificação de Admin
# ============================================
def admin_required(f):
    """Decorador que exige perfil de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Acesso negado. Área restrita a administradores.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================
# ROTAS PÚBLICAS
# ============================================

@app.route('/')
def index():
    """Página inicial - redireciona conforme perfil do usuário"""
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('paciente_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login do sistema"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        
        # Busca usuário pelo email
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_password(senha):
            if not usuario.ativo:
                flash('Sua conta está desativada. Entre em contato com o consultório.', 'warning')
                return render_template('login.html')
            
            login_user(usuario)
            flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
            
            # Redireciona para página apropriada
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('index'))
        else:
            flash('Email ou senha inválidos.', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Página de cadastro de novos pacientes"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        cpf = request.form.get('cpf', '').strip()
        senha = request.form.get('senha', '')
        confirmar_senha = request.form.get('confirmar_senha', '')
        
        # Validações
        erros = []
        
        if not nome or len(nome) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres.')
        
        if not email or '@' not in email:
            erros.append('Email inválido.')
        elif Usuario.query.filter_by(email=email).first():
            erros.append('Este email já está cadastrado.')
        
        if cpf and Usuario.query.filter_by(cpf=cpf).first():
            erros.append('Este CPF já está cadastrado.')
        
        if len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')
        
        if senha != confirmar_senha:
            erros.append('As senhas não conferem.')
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('register.html')
        
        # Cria novo usuário
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf if cpf else None,
            perfil='paciente'
        )
        novo_usuario.set_password(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    """Encerra a sessão do usuário"""
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))


# ============================================
# ROTAS DO PACIENTE
# ============================================

@app.route('/paciente')
@login_required
def paciente_dashboard():
    """Dashboard do paciente"""
    # Busca próximos agendamentos do paciente
    agendamentos = Agendamento.query.filter_by(
        paciente_id=current_user.id
    ).filter(
        Agendamento.data_hora_inicio >= datetime.now()
    ).order_by(
        Agendamento.data_hora_inicio
    ).limit(5).all()
    
    # Contadores para estatísticas
    total_agendamentos = Agendamento.query.filter_by(paciente_id=current_user.id).count()
    agendamentos_confirmados = Agendamento.query.filter_by(
        paciente_id=current_user.id, 
        status='confirmado'
    ).count()
    
    return render_template('paciente/dashboard.html', 
                         agendamentos=agendamentos,
                         total_agendamentos=total_agendamentos,
                         agendamentos_confirmados=agendamentos_confirmados)


@app.route('/paciente/meus-agendamentos')
@login_required
def meus_agendamentos():
    """Lista todos os agendamentos do paciente"""
    agendamentos = Agendamento.query.filter_by(
        paciente_id=current_user.id
    ).order_by(
        Agendamento.data_hora_inicio.desc()
    ).all()
    
    return render_template('paciente/meus_agendamentos.html', agendamentos=agendamentos)


@app.route('/paciente/agendar', methods=['GET', 'POST'])
@login_required
def agendar():
    """Página de novo agendamento"""
    servicos = Servico.query.filter_by(ativo=True).all()
    dentistas = Dentista.query.filter_by(ativo=True).all()
    
    if request.method == 'POST':
        servico_id = request.form.get('servico_id')
        dentista_id = request.form.get('dentista_id')
        data = request.form.get('data')
        hora = request.form.get('hora')
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações básicas
        if not all([servico_id, dentista_id, data, hora]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)
        
        # Converte data e hora
        try:
            data_hora_inicio = datetime.strptime(f'{data} {hora}', '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Data ou hora inválida.', 'danger')
            return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)
        
        # Verifica se a data é futura
        if data_hora_inicio <= datetime.now():
            flash('Não é possível agendar para datas passadas.', 'danger')
            return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)
        
        # Busca serviço para calcular duração
        servico = Servico.query.get(servico_id)
        if not servico:
            flash('Serviço não encontrado.', 'danger')
            return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)
        
        data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        
        # Verifica disponibilidade do dentista
        conflito = Agendamento.query.filter(
            Agendamento.dentista_id == dentista_id,
            Agendamento.status.in_(['pendente', 'confirmado']),
            Agendamento.data_hora_inicio < data_hora_fim,
            Agendamento.data_hora_fim > data_hora_inicio
        ).first()
        
        if conflito:
            flash('Este horário não está disponível. Por favor, escolha outro.', 'warning')
            return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)
        
        # Cria o agendamento
        novo_agendamento = Agendamento(
            paciente_id=current_user.id,
            dentista_id=dentista_id,
            servico_id=servico_id,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            observacoes=observacoes,
            status='pendente'
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento realizado com sucesso! Aguarde a confirmação.', 'success')
        return redirect(url_for('meus_agendamentos'))
    
    return render_template('paciente/agendar.html', servicos=servicos, dentistas=dentistas)


@app.route('/paciente/cancelar/<int:id>', methods=['POST'])
@login_required
def cancelar_agendamento(id):
    """Cancela um agendamento do paciente"""
    agendamento = Agendamento.query.get_or_404(id)
    
    # Verifica se o agendamento pertence ao paciente
    if agendamento.paciente_id != current_user.id:
        flash('Você não tem permissão para cancelar este agendamento.', 'danger')
        return redirect(url_for('meus_agendamentos'))
    
    # Verifica se ainda pode cancelar
    if agendamento.status in ['cancelado', 'concluido']:
        flash('Este agendamento não pode ser cancelado.', 'warning')
        return redirect(url_for('meus_agendamentos'))
    
    agendamento.status = 'cancelado'
    db.session.commit()
    
    flash('Agendamento cancelado com sucesso.', 'success')
    return redirect(url_for('meus_agendamentos'))


# ============================================
# ROTAS DO ADMINISTRADOR
# ============================================

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Dashboard do administrador"""
    # Filtros de data
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    hoje = datetime.now().date()
    
    if data_inicio_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
        except ValueError:
            data_inicio = hoje.replace(day=1)
    else:
        data_inicio = hoje.replace(day=1) # Início do mês atual
        
    if data_fim_str:
        try:
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
        except ValueError:
            data_fim = hoje
    else:
        data_fim = hoje # Até hoje

    # Estatísticas gerais
    total_pacientes = Usuario.query.filter_by(perfil='paciente').count()
    total_dentistas = Dentista.query.filter_by(ativo=True).count()
    total_servicos = Servico.query.filter_by(ativo=True).count()
    
    # Agendamentos de hoje
    agendamentos_hoje = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora_inicio) == hoje
    ).order_by(Agendamento.data_hora_inicio).all()
    
    # Agendamentos pendentes
    pendentes = Agendamento.query.filter_by(status='pendente').count()
    
    # Cálculo de Receita e Agendamentos no Período
    agendamentos_periodo = Agendamento.query.filter(
        db.func.date(Agendamento.data_hora_inicio) >= data_inicio,
        db.func.date(Agendamento.data_hora_inicio) <= data_fim
    ).all()
    
    total_agendamentos_periodo = len(agendamentos_periodo)
    receita_total = 0.0
    
    for ag in agendamentos_periodo:
        if ag.status == 'concluido':
             if ag.servico:
                receita_total += float(ag.servico.preco)
    
    return render_template('admin/dashboard.html',
                         total_pacientes=total_pacientes,
                         total_dentistas=total_dentistas,
                         total_servicos=total_servicos,
                         agendamentos_hoje=agendamentos_hoje,
                         pendentes=pendentes,
                         receita_total=receita_total,
                         total_agendamentos_periodo=total_agendamentos_periodo,
                         data_inicio=data_inicio,
                         data_fim=data_fim)


@app.route('/admin/agenda')
@login_required
@admin_required
def admin_agenda():
    """Visualização completa da agenda"""
    # Filtros
    data_filtro = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    dentista_filtro = request.args.get('dentista_id')
    status_filtro = request.args.get('status')
    
    # Query base
    query = Agendamento.query
    
    # Aplica filtros
    if data_filtro:
        try:
            data = datetime.strptime(data_filtro, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Agendamento.data_hora_inicio) == data)
        except ValueError:
            pass
    
    if dentista_filtro:
        query = query.filter_by(dentista_id=dentista_filtro)
    
    if status_filtro:
        query = query.filter_by(status=status_filtro)
    
    agendamentos = query.order_by(Agendamento.data_hora_inicio).all()
    dentistas = Dentista.query.filter_by(ativo=True).all()
    
    return render_template('admin/agenda.html',
                         agendamentos=agendamentos,
                         dentistas=dentistas,
                         data_filtro=data_filtro,
                         dentista_filtro=dentista_filtro,
                         status_filtro=status_filtro)


@app.route('/admin/agendamento/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def atualizar_status_agendamento(id):
    """Atualiza o status de um agendamento (aprovar/rejeitar)"""
    agendamento = Agendamento.query.get_or_404(id)
    novo_status = request.form.get('status')
    
    if novo_status in ['confirmado', 'cancelado', 'concluido']:
        agendamento.status = novo_status
        db.session.commit()
        flash(f'Status atualizado para: {novo_status}', 'success')
    else:
        flash('Status inválido.', 'danger')
    
    return redirect(url_for('admin_agenda'))


@app.route('/admin/agendamento/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_novo_agendamento():
    """Página de novo agendamento pelo admin"""
    pacientes = Usuario.query.filter_by(perfil='paciente', ativo=True).all()
    servicos = Servico.query.filter_by(ativo=True).all()
    dentistas = Dentista.query.filter_by(ativo=True).all()
    
    if request.method == 'POST':
        paciente_id = request.form.get('paciente_id')
        servico_id = request.form.get('servico_id')
        dentista_id = request.form.get('dentista_id')
        data = request.form.get('data')
        hora = request.form.get('hora')
        observacoes = request.form.get('observacoes', '').strip()
        
        # Validações básicas
        if not all([paciente_id, servico_id, dentista_id, data, hora]):
            flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
            return render_template('admin/agendamento_form.html', 
                                 pacientes=pacientes, 
                                 servicos=servicos, 
                                 dentistas=dentistas)
        
        # Converte data e hora
        try:
            data_hora_inicio = datetime.strptime(f'{data} {hora}', '%Y-%m-%d %H:%M')
        except ValueError:
            flash('Data ou hora inválida.', 'danger')
            return render_template('admin/agendamento_form.html', 
                                 pacientes=pacientes, 
                                 servicos=servicos, 
                                 dentistas=dentistas)
        
        # Busca serviço para calcular duração
        servico = Servico.query.get(servico_id)
        if not servico:
            flash('Serviço não encontrado.', 'danger')
            return render_template('admin/agendamento_form.html', 
                                 pacientes=pacientes, 
                                 servicos=servicos, 
                                 dentistas=dentistas)
        
        data_hora_fim = data_hora_inicio + timedelta(minutes=servico.duracao_minutos)
        
        # Verifica disponibilidade do dentista
        conflito = Agendamento.query.filter(
            Agendamento.dentista_id == dentista_id,
            Agendamento.status.in_(['pendente', 'confirmado']),
            Agendamento.data_hora_inicio < data_hora_fim,
            Agendamento.data_hora_fim > data_hora_inicio
        ).first()
        
        if conflito:
            flash('Este horário não está disponível. Por favor, escolha outro.', 'warning')
            return render_template('admin/agendamento_form.html', 
                                 pacientes=pacientes, 
                                 servicos=servicos, 
                                 dentistas=dentistas)
        
        # Cria o agendamento já confirmado (admin não precisa aprovação)
        novo_agendamento = Agendamento(
            paciente_id=paciente_id,
            dentista_id=dentista_id,
            servico_id=servico_id,
            data_hora_inicio=data_hora_inicio,
            data_hora_fim=data_hora_fim,
            observacoes=observacoes,
            status='confirmado'  # Admin já confirma direto
        )
        
        db.session.add(novo_agendamento)
        db.session.commit()
        
        flash('Agendamento criado com sucesso!', 'success')
        return redirect(url_for('admin_agenda'))
    
    return render_template('admin/agendamento_form.html', 
                         pacientes=pacientes, 
                         servicos=servicos, 
                         dentistas=dentistas)



# ============================================
# CRUD: Serviços
# ============================================

@app.route('/admin/servicos')
@login_required
@admin_required
def admin_servicos():
    """Lista todos os serviços"""
    servicos = Servico.query.all()
    return render_template('admin/servicos.html', servicos=servicos)


@app.route('/admin/servicos/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_servico():
    """Cadastra novo serviço"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        descricao = request.form.get('descricao', '').strip()
        duracao = request.form.get('duracao_minutos', 30, type=int)
        preco = request.form.get('preco', '0').replace(',', '.')
        
        try:
            preco = float(preco)
        except ValueError:
            preco = 0.0
        
        servico = Servico(
            nome=nome,
            descricao=descricao,
            duracao_minutos=duracao,
            preco=preco
        )
        
        db.session.add(servico)
        db.session.commit()
        
        flash('Serviço cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_servicos'))
    
    return render_template('admin/servico_form.html', servico=None)


@app.route('/admin/servicos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_servico(id):
    """Edita um serviço existente"""
    servico = Servico.query.get_or_404(id)
    
    if request.method == 'POST':
        servico.nome = request.form.get('nome', '').strip()
        servico.descricao = request.form.get('descricao', '').strip()
        servico.duracao_minutos = request.form.get('duracao_minutos', 30, type=int)
        
        preco = request.form.get('preco', '0').replace(',', '.')
        try:
            servico.preco = float(preco)
        except ValueError:
            servico.preco = 0.0
        
        servico.ativo = 'ativo' in request.form
        
        db.session.commit()
        
        flash('Serviço atualizado com sucesso!', 'success')
        return redirect(url_for('admin_servicos'))
    
    return render_template('admin/servico_form.html', servico=servico)


@app.route('/admin/servicos/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_servico(id):
    """Exclui um serviço"""
    servico = Servico.query.get_or_404(id)
    
    # Verifica se há agendamentos vinculados
    if servico.agendamentos:
        flash('Não é possível excluir este serviço pois há agendamentos vinculados.', 'warning')
        return redirect(url_for('admin_servicos'))
    
    db.session.delete(servico)
    db.session.commit()
    
    flash('Serviço excluído com sucesso!', 'success')
    return redirect(url_for('admin_servicos'))


# ============================================
# CRUD: Dentistas
# ============================================

@app.route('/admin/dentistas')
@login_required
@admin_required
def admin_dentistas():
    """Lista todos os dentistas"""
    dentistas = Dentista.query.all()
    return render_template('admin/dentistas.html', dentistas=dentistas)


@app.route('/admin/dentistas/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_dentista():
    """Cadastra novo dentista"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        cro = request.form.get('cro', '').strip()
        especialidade = request.form.get('especialidade', '').strip()
        
        # Verifica se CRO já existe
        if Dentista.query.filter_by(cro=cro).first():
            flash('Este CRO já está cadastrado.', 'danger')
            return render_template('admin/dentista_form.html', dentista=None)
        
        dentista = Dentista(
            nome=nome,
            cro=cro,
            especialidade=especialidade
        )
        
        db.session.add(dentista)
        db.session.commit()
        
        flash('Dentista cadastrado com sucesso!', 'success')
        return redirect(url_for('admin_dentistas'))
    
    return render_template('admin/dentista_form.html', dentista=None)


@app.route('/admin/dentistas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_dentista(id):
    """Edita um dentista existente"""
    dentista = Dentista.query.get_or_404(id)
    
    if request.method == 'POST':
        dentista.nome = request.form.get('nome', '').strip()
        dentista.especialidade = request.form.get('especialidade', '').strip()
        dentista.ativo = 'ativo' in request.form
        
        # CRO não pode ser alterado
        
        db.session.commit()
        
        flash('Dentista atualizado com sucesso!', 'success')
        return redirect(url_for('admin_dentistas'))
    
    return render_template('admin/dentista_form.html', dentista=dentista)


@app.route('/admin/dentistas/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_dentista(id):
    """Exclui um dentista"""
    dentista = Dentista.query.get_or_404(id)
    
    # Verifica se há agendamentos vinculados
    if dentista.agendamentos:
        flash('Não é possível excluir este dentista pois há agendamentos vinculados.', 'warning')
        return redirect(url_for('admin_dentistas'))
    
    db.session.delete(dentista)
    db.session.commit()
    
    flash('Dentista excluído com sucesso!', 'success')
    return redirect(url_for('admin_dentistas'))


# ============================================
# CRUD: Pacientes
# ============================================

@app.route('/admin/pacientes')
@login_required
@admin_required
def admin_pacientes():
    """Lista todos os pacientes"""
    pacientes = Usuario.query.filter_by(perfil='paciente').all()
    return render_template('admin/pacientes.html', pacientes=pacientes)


@app.route('/admin/pacientes/<int:id>')
@login_required
@admin_required
def ver_paciente(id):
    """Visualiza detalhes de um paciente"""
    paciente = Usuario.query.get_or_404(id)
    agendamentos = Agendamento.query.filter_by(paciente_id=id).order_by(
        Agendamento.data_hora_inicio.desc()
    ).all()
    return render_template('admin/paciente_detalhe.html', paciente=paciente, agendamentos=agendamentos)


@app.route('/admin/pacientes/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_paciente_status(id):
    """Ativa/desativa um paciente"""
    paciente = Usuario.query.get_or_404(id)
    paciente.ativo = not paciente.ativo
    db.session.commit()
    
    status = 'ativado' if paciente.ativo else 'desativado'
    flash(f'Paciente {status} com sucesso!', 'success')
    return redirect(url_for('admin_pacientes'))


@app.route('/admin/pacientes/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo_paciente():
    """Cadastra novo paciente pelo admin"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        telefone = request.form.get('telefone', '').strip()
        cpf = request.form.get('cpf', '').strip()
        senha = request.form.get('senha', '')
        
        # Validações
        erros = []
        
        if not nome or len(nome) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres.')
        
        if not email or '@' not in email:
            erros.append('Email inválido.')
        elif Usuario.query.filter_by(email=email).first():
            erros.append('Este email já está cadastrado.')
        
        if cpf and Usuario.query.filter_by(cpf=cpf).first():
            erros.append('Este CPF já está cadastrado.')
        
        if len(senha) < 6:
            erros.append('A senha deve ter pelo menos 6 caracteres.')
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('admin/paciente_form.html', paciente=None)
        
        # Cria novo paciente
        novo_paciente = Usuario(
            nome=nome,
            email=email,
            telefone=telefone,
            cpf=cpf if cpf else None,
            perfil='paciente'
        )
        novo_paciente.set_password(senha)
        
        db.session.add(novo_paciente)
        db.session.commit()
        
        flash(f'Paciente cadastrado com sucesso! Login: {email} / Senha: {senha}', 'success')
        return redirect(url_for('admin_pacientes'))
    
    return render_template('admin/paciente_form.html', paciente=None)


@app.route('/admin/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_paciente(id):
    """Edita um paciente existente"""
    paciente = Usuario.query.get_or_404(id)
    
    if request.method == 'POST':
        paciente.nome = request.form.get('nome', '').strip()
        paciente.telefone = request.form.get('telefone', '').strip()
        
        # Email e CPF não podem ser alterados para evitar conflitos
        
        # Se uma nova senha foi fornecida, atualiza
        nova_senha = request.form.get('senha', '').strip()
        if nova_senha and len(nova_senha) >= 6:
            paciente.set_password(nova_senha)
            flash('Senha atualizada!', 'info')
        
        paciente.ativo = 'ativo' in request.form
        
        db.session.commit()
        
        flash('Paciente atualizado com sucesso!', 'success')
        return redirect(url_for('admin_pacientes'))
    
    return render_template('admin/paciente_form.html', paciente=paciente)



# ============================================
# API: Horários Disponíveis
# ============================================

@app.route('/api/horarios-disponiveis')
@login_required
def horarios_disponiveis():
    """Retorna horários disponíveis para agendamento"""
    dentista_id = request.args.get('dentista_id', type=int)
    data = request.args.get('data')
    servico_id = request.args.get('servico_id', type=int)
    
    if not all([dentista_id, data, servico_id]):
        return jsonify({'error': 'Parâmetros inválidos'}), 400
    
    try:
        data_selecionada = datetime.strptime(data, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Data inválida'}), 400
    
    # Busca serviço para a duração
    servico = Servico.query.get(servico_id)
    if not servico:
        return jsonify({'error': 'Serviço não encontrado'}), 404
    
    # Busca configurações da clínica
    config = Configuracao.query.first()
    if not config:
        config = Configuracao()
    
    # Verifica se o dia da semana está habilitado
    dia_semana = data_selecionada.weekday()  # 0=Segunda, 6=Domingo
    dias_habilitados = {
        0: config.segunda,
        1: config.terca,
        2: config.quarta,
        3: config.quinta,
        4: config.sexta,
        5: config.sabado,
        6: config.domingo
    }
    
    if not dias_habilitados.get(dia_semana, False):
        return jsonify({'horarios': [], 'mensagem': 'Clínica fechada neste dia'})
    
    # Gera horários com base nas configurações (manhã e tarde)
    horarios_base = []
    intervalo = config.intervalo_consultas or 30
    
    # Parse dos horários configurados
    def parse_hora(hora_str):
        try:
            h, m = map(int, hora_str.split(':'))
            return h, m
        except:
            return 8, 0
    
    # Turno da manhã
    h_ini_m, m_ini_m = parse_hora(config.hora_inicio_manha or '08:00')
    h_fim_m, m_fim_m = parse_hora(config.hora_fim_manha or '12:00')
    hora_atual = datetime.combine(data_selecionada, datetime.min.time().replace(hour=h_ini_m, minute=m_ini_m))
    hora_final_manha = datetime.combine(data_selecionada, datetime.min.time().replace(hour=h_fim_m, minute=m_fim_m))
    
    while hora_atual < hora_final_manha:
        horarios_base.append(hora_atual)
        hora_atual += timedelta(minutes=intervalo)
    
    # Turno da tarde
    h_ini_t, m_ini_t = parse_hora(config.hora_inicio_tarde or '14:00')
    h_fim_t, m_fim_t = parse_hora(config.hora_fim_tarde or '18:00')
    hora_atual = datetime.combine(data_selecionada, datetime.min.time().replace(hour=h_ini_t, minute=m_ini_t))
    hora_final_tarde = datetime.combine(data_selecionada, datetime.min.time().replace(hour=h_fim_t, minute=m_fim_t))
    
    while hora_atual < hora_final_tarde:
        horarios_base.append(hora_atual)
        hora_atual += timedelta(minutes=intervalo)
    
    # Busca agendamentos do dia para o dentista
    agendamentos_dia = Agendamento.query.filter(
        Agendamento.dentista_id == dentista_id,
        Agendamento.status.in_(['pendente', 'confirmado']),
        db.func.date(Agendamento.data_hora_inicio) == data_selecionada
    ).all()
    
    # Filtra horários indisponíveis
    horarios_disponiveis = []
    for horario in horarios_base:
        hora_fim = horario + timedelta(minutes=servico.duracao_minutos)
        
        # Verifica conflito
        conflito = False
        for ag in agendamentos_dia:
            if horario < ag.data_hora_fim and hora_fim > ag.data_hora_inicio:
                conflito = True
                break
        
        if not conflito:
            horarios_disponiveis.append(horario.strftime('%H:%M'))
    
    return jsonify({'horarios': horarios_disponiveis})


# ============================================
# CONFIGURAÇÕES DA CLÍNICA
# ============================================

@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_configuracoes():
    """Página de configurações da clínica"""
    # Busca ou cria configuração
    config = Configuracao.query.first()
    if not config:
        config = Configuracao()
        db.session.add(config)
        db.session.commit()
    
    if request.method == 'POST':
        # Atualiza dados da clínica
        config.nome_clinica = request.form.get('nome_clinica', '').strip()
        config.telefone_clinica = request.form.get('telefone_clinica', '').strip()
        config.endereco_clinica = request.form.get('endereco_clinica', '').strip()
        
        # Atualiza horários dos turnos
        config.hora_inicio_manha = request.form.get('hora_inicio_manha', '08:00')
        config.hora_fim_manha = request.form.get('hora_fim_manha', '12:00')
        config.hora_inicio_tarde = request.form.get('hora_inicio_tarde', '14:00')
        config.hora_fim_tarde = request.form.get('hora_fim_tarde', '18:00')
        config.intervalo_consultas = request.form.get('intervalo_consultas', 30, type=int)
        
        # Atualiza dias da semana
        config.segunda = 'segunda' in request.form
        config.terca = 'terca' in request.form
        config.quarta = 'quarta' in request.form
        config.quinta = 'quinta' in request.form
        config.sexta = 'sexta' in request.form
        config.sabado = 'sabado' in request.form
        config.domingo = 'domingo' in request.form
        
        db.session.commit()
        flash('Configurações atualizadas com sucesso!', 'success')
        return redirect(url_for('admin_configuracoes'))
    
    return render_template('admin/configuracoes.html', config=config)


# ============================================
# INICIALIZAÇÃO DO SISTEMA
# ============================================

def init_database():
    """Inicializa o banco de dados e cria dados de exemplo"""
    with app.app_context():
        # ATENÇÃO: Se o banco já tiver tabelas antigas, precisamos recriá-las
        # Isso é necessário apenas na primeira execução após atualizar os modelos
        # Em produção, usar ferramentas de migração como Flask-Migrate
        try:
            # Tenta verificar se as tabelas têm a estrutura nova
            Usuario.query.filter_by(perfil='admin').first()
        except Exception as e:
            print(f'Recriando tabelas do banco de dados...')
            print(f'Motivo: {e}')
            # Faz rollback da transação com erro
            db.session.rollback()
            # Se der erro, significa que a estrutura está diferente
            # Recria todas as tabelas (CUIDADO: isso apaga dados existentes)
            db.drop_all()
            db.create_all()
            print('Tabelas recriadas com sucesso!')
        
        # Verifica se já existe um admin
        if not Usuario.query.filter_by(perfil='admin').first():
            print('Criando usuário administrador padrão...')
            admin = Usuario(
                nome='Administrador',
                email='admin@dentalsystem.com',
                perfil='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin criado: admin@dentalsystem.com / admin123')
        
        # Cria serviços de exemplo se não existirem
        if not Servico.query.first():
            print('Criando serviços de exemplo...')
            servicos = [
                Servico(nome='Limpeza', descricao='Limpeza dental completa', duracao_minutos=30, preco=100.00),
                Servico(nome='Consulta', descricao='Consulta de avaliação', duracao_minutos=30, preco=80.00),
                Servico(nome='Clareamento', descricao='Clareamento dental', duracao_minutos=60, preco=500.00),
                Servico(nome='Restauração', descricao='Restauração de dente', duracao_minutos=45, preco=150.00),
                Servico(nome='Extração', descricao='Extração dentária simples', duracao_minutos=30, preco=200.00),
            ]
            db.session.add_all(servicos)
            db.session.commit()
            print('Serviços de exemplo criados!')
        
        # Cria dentista de exemplo se não existir
        if not Dentista.query.first():
            print('Criando dentista de exemplo...')
            dentista = Dentista(
                nome='Dr. Carlos Silva',
                cro='12345-SP',
                especialidade='Clínico Geral'
            )
            db.session.add(dentista)
            db.session.commit()
            print('Dentista de exemplo criado!')
        
        # Cria configuração padrão se não existir
        try:
            if not Configuracao.query.first():
                print('Criando configurações padrão...')
                config = Configuracao(
                    nome_clinica='DentalSystem',
                    hora_inicio_manha='08:00',
                    hora_fim_manha='12:00',
                    hora_inicio_tarde='14:00',
                    hora_fim_tarde='18:00',
                    intervalo_consultas=30
                )
                db.session.add(config)
                db.session.commit()
                print('Configurações padrão criadas!')
        except Exception as e:
            print(f'Erro ao criar configurações, recriando tabela: {e}')
            db.session.rollback()
            # Cria apenas a tabela de configurações
            Configuracao.__table__.create(db.engine, checkfirst=True)
            # Tenta criar novamente
            config = Configuracao(
                nome_clinica='DentalSystem',
                hora_inicio_manha='08:00',
                hora_fim_manha='12:00',
                hora_inicio_tarde='14:00',
                hora_fim_tarde='18:00',
                intervalo_consultas=30
            )
            db.session.add(config)
            db.session.commit()
            print('Tabela de configurações criada e populada!')
        
        print('Banco de dados inicializado com sucesso!')


if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
