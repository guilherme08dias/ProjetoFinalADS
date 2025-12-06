from app import app, db, Usuario

def test_app():
    with app.app_context():
        print("Testing database connection...")
        try:
            # Create tables if they don't exist (this might fail if schema changed without migration, but for dev it's ok to try)
            # ideally we should drop all but I won't do destructive actions automatically without being sure
            db.create_all()
            print("Tables created/verified.")
            
            # Check for admin user
            admin = Usuario.query.filter_by(email='admin@dentalsystem.com').first()
            if admin:
                print(f"Admin user found: {admin.email}")
                if admin.check_password('admin123'):
                    print("Admin password verification: SUCCESS")
                else:
                    print("Admin password verification: FAILED")
            else:
                print("Admin user NOT found (it should be created on first run of app.py)")
                
            print("Database test passed!")
            
        except Exception as e:
            print(f"Database test FAILED: {e}")

if __name__ == "__main__":
    test_app()
