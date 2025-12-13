"""
Arquivo WSGI para producao - DentalSystem
Este arquivo e usado pelo Gunicorn para servir a aplicacao
"""

from app import app

if __name__ == "__main__":
    app.run()
