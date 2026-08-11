from datetime import datetime, timezone, timedelta
from app.db.session import SessionLocal
from app.db.models import Email
from app.services.gmail_service import get_gmail_service
from app.services.pending_mover_service import move_stale_newsletters_to_pending

db = SessionLocal()

# TRUCO SOLO PARA PROBAR: forzamos que el correo de Duolingo parezca tener 8 dias sin leer
email_prueba = db.query(Email).filter(Email.sender.contains("duolingo")).first()
if email_prueba:
    email_prueba.first_seen_unread_at = datetime.now(timezone.utc) - timedelta(days=8)
    db.commit()
    print(f"Correo de prueba modificado: first_seen_unread_at = {email_prueba.first_seen_unread_at}")
else:
    print("No se encontro el correo de Duolingo, corre primero test_orchestrator.py")

gmail_service = get_gmail_service()
movidos = move_stale_newsletters_to_pending(db, gmail_service)

print(f"\nCorreos movidos a Pendientes: {len(movidos)}")
for email in movidos:
    print(f"  - {email.subject}")

db.close()