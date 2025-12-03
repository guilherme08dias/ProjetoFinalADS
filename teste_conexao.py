from sqlalchemy import create_engine, text

# Configuração (Senha 1234)
# Se der erro, tente trocar 'localhost' por '127.0.0.1'
DB_URI = 'postgresql://postgres:1234@localhost:5432/dentalsystem'

print(f"--- INICIANDO TESTE DE CONEXÃO ---")
print(f"Tentando conectar em: {DB_URI}")

try:
    engine = create_engine(DB_URI)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("\n✅ SUCESSO! CONEXÃO FUNCIONANDO PERFEITAMENTE.")
        print("O banco de dados existe e a senha está correta.")
except Exception as e:
    print("\n❌ FALHA NA CONEXÃO.")
    print("ERRO ENCONTRADO:")
    print(e)
    print("\n------------------------------------------------")
    print("DICAS PARA RESOLVER:")
    if "password authentication failed" in str(e):
        print("1. A senha '1234' está incorreta. Verifique qual senha você colocou no Postgres.")
    elif "does not exist" in str(e):
        print("2. O banco de dados 'dentalsystem' não existe. Crie ele no pgAdmin.")
    elif "Connection refused" in str(e):
        print("3. O PostgreSQL não está rodando ou não está na porta 5432.")