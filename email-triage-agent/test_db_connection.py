from app.db.session import engine

try:
    connection = engine.connect()
    print("✅ Conexión exitosa a PostgreSQL")
    connection.close()
except Exception as e:
    print(f"❌ Error de conexión: {e}")