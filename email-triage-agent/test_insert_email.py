from app.db.session import SessionLocal
from app.db.models import Email
from datetime import datetime, timezone

db = SessionLocal()

# Esto SÍ debería funcionar (valor válido)
try:
    test_email = Email(
        gmail_message_id="test123",
        sender="test@test.com",
        subject="Correo de prueba",
        category="spam",
        received_at=datetime.now(timezone.utc)
    )
    db.add(test_email)
    db.commit()
    print("✅ Insert válido funcionó correctamente")
except Exception as e:
    print(f"❌ Falló insert válido (no debería pasar): {e}")
    db.rollback()

db.close()