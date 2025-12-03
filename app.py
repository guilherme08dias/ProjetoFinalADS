import os
from flask import Flask, render_template, request, redirect, url_for
from models import db, Usuario, Agendamento

app = Flask(__name__)

# --- CONFIGURAÇÃO DO BANCO DE DADOS ---
# ATENÇÃO: Se sua senha do Postgres não for '1234', troque aqui!
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost:5432/dentalsystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    if not os.path.exists('templates'):
        return "ERRO: Pasta 'templates' não encontrada! Crie a pasta e coloque os arquivos HTML dentro."
    
    try:
        agendamentos = Agendamento.query.all()
        return render_template('index.html', agendamentos=agendamentos)
    except Exception as e:
        return f"ERRO DE BANCO DE DADOS: {str(e)}. Verifique se o PostgreSQL está rodando e se criou o banco 'dentalsystem'."

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        # Validação Real no Banco
        user = Usuario.query.filter_by(email=email).first()
        if user and user.senha == senha:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="Email ou senha inválidos")
    return render_template('login.html')

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all() # Cria tabelas automaticamente
            
            # Cria usuário admin se não existir (Seed)
            if not Usuario.query.filter_by(email='admin@dentalsystem.com').first():
                print("Criando usuário admin padrão...")
                admin = Usuario(nome='Administrador', email='admin@dentalsystem.com', senha='admin')
                db.session.add(admin)
                db.session.commit()
            print("Banco de dados conectado e tabelas verificadas!")
        except Exception as e:
            print(f"ERRO AO CONECTAR NO BANCO: {e}")
            
    app.run(debug=True)