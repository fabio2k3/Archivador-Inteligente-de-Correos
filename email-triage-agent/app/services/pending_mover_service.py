from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.db.models import Email, EmailCategory
from app.services.gmail_service import get_or_create_pendientes_label, apply_label_to_message

DIAS_LIMITE = 7


def move_stale_newsletters_to_pending(db: Session, gmail_service) -> list[Email]:
    """
    Busca correos tipo newsletter con mas de 7 dias sin leer que aun
    no han sido movidos a Pendientes, les aplica el label, y actualiza
    el registro en la base de datos.
    """
    limite_fecha = datetime.now(timezone.utc) - timedelta(days=DIAS_LIMITE)

    candidatos = db.query(Email).filter(
        Email.category == EmailCategory.NEWSLETTER,
        Email.first_seen_unread_at.isnot(None),
        Email.first_seen_unread_at <= limite_fecha,
        Email.moved_to_pending == False,
    ).all()

    if not candidatos:
        return []

    label_id = get_or_create_pendientes_label(gmail_service)
    movidos = []

    for email in candidatos:
        apply_label_to_message(gmail_service, email.gmail_message_id, label_id)
        email.moved_to_pending = True
        movidos.append(email)

    db.commit()
    return movidos