import logging
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.core.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

celery_app = Celery(
    "email_triage_agent",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.timezone = "America/Guayaquil"  # ajusta a tu zona horaria real

celery_app.conf.beat_schedule = {
    "sync-emails-every-30-minutes": {
        "task": "app.tasks.celery_tasks.sync_and_process_emails",
        "schedule": crontab(minute="*/30"),
    },
}


@celery_app.task(name="app.tasks.celery_tasks.sync_and_process_emails")
def sync_and_process_emails():
    """
    Tarea periodica: sincroniza correos recientes de Gmail, los procesa
    con IA, los clasifica, y mueve newsletters con +7 dias a Pendientes.
    """
    from app.db.session import SessionLocal
    from app.services.gmail_service import get_gmail_service
    from app.services.email_orchestrator import process_and_store_email
    from app.services.pending_mover_service import move_stale_newsletters_to_pending

    db = SessionLocal()
    gmail_service = get_gmail_service()

    try:
        results = gmail_service.users().messages().list(
            userId="me", maxResults=20
        ).execute()
        messages = results.get("messages", [])

        procesados = 0
        fallidos = 0

        for msg in messages:
            try:
                full_message = gmail_service.users().messages().get(
                    userId="me", id=msg["id"], format="full"
                ).execute()
                is_unread = "UNREAD" in full_message.get("labelIds", [])
                process_and_store_email(db, full_message, is_unread)
                procesados += 1
            except Exception as e:
                logger.error(f"Error procesando correo {msg['id']}: {e}")
                fallidos += 1
                continue

        movidos = move_stale_newsletters_to_pending(db, gmail_service)

        resultado = f"Procesados: {procesados}, Fallidos: {fallidos}, Movidos a Pendientes: {len(movidos)}"
        logger.info(resultado)
        return resultado

    finally:
        db.close()