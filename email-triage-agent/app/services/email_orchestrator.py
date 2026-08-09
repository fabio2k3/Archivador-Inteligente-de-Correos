from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.db.models import Email, EmailCategory
from app.services.ai_service import analyze_email
from app.services.classification_service import classify_email


def process_and_store_email(db: Session, gmail_message: dict, is_unread: bool) -> Email:
    """
    Procesa un correo de Gmail: verifica si ya existe en la DB, si no,
    lo analiza con IA, lo clasifica, y lo guarda.
    """
    gmail_id = gmail_message["id"]

    # Evitar reprocesar un correo que ya guardamos antes
    existing = db.query(Email).filter(Email.gmail_message_id == gmail_id).first()

    headers = gmail_message["payload"]["headers"]
    sender = next((h["value"] for h in headers if h["name"] == "From"), "")
    subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
    body = gmail_message.get("snippet", "")  # usamos el snippet por ahora (extracto corto)

    if existing:
        # Solo actualizamos first_seen_unread_at si aun no se habia marcado
        if is_unread and existing.first_seen_unread_at is None:
            existing.first_seen_unread_at = datetime.now(timezone.utc)
            db.commit()
        return existing

    # Correo nuevo: lo analizamos con IA
    ai_result = analyze_email(subject=subject, sender=sender, body=body)

    classification = classify_email(
        sender=sender,
        subject=subject,
        body=body,
        ai_suggested_category=ai_result["suggested_category"],
    )

    new_email = Email(
        gmail_message_id=gmail_id,
        gmail_thread_id=gmail_message.get("threadId"),
        sender=sender,
        subject=subject,
        received_at=datetime.now(timezone.utc),  # ajustaremos esto con la fecha real del header en el siguiente paso
        category=EmailCategory(classification["final_category"]),
        summary=" | ".join(ai_result["summary_bullets"]),
        due_date=ai_result["due_date"],
        first_seen_unread_at=datetime.now(timezone.utc) if is_unread else None,
        processed_by_ai=True,
    )

    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    return new_email