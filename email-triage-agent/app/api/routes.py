from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.session import get_db
from app.db.models import Email, EmailCategory
from app.api.schemas import EmailResponse, SyncTriggerResponse

router = APIRouter()


@router.get("/emails", response_model=list[EmailResponse])
def list_emails(
    category: EmailCategory | None = Query(None, description="Filtrar por categoria"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """Lista los correos procesados, mas recientes primero."""
    query = db.query(Email)
    if category:
        query = query.filter(Email.category == category)
    return query.order_by(desc(Email.received_at)).limit(limit).all()


@router.get("/emails/pending", response_model=list[EmailResponse])
def list_pending_emails(db: Session = Depends(get_db)):
    """Lista los correos que ya fueron movidos a la carpeta Pendientes."""
    return db.query(Email).filter(Email.moved_to_pending == True).all()


@router.get("/emails/{email_id}", response_model=EmailResponse)
def get_email(email_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de un correo especifico por su ID interno."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Correo no encontrado")
    return email


@router.post("/sync/trigger", response_model=SyncTriggerResponse)
def trigger_manual_sync():
    """
    Dispara la sincronizacion de correos manualmente, sin esperar
    a que Celery Beat lo haga automaticamente cada 30 minutos.
    """
    from app.tasks.celery_tasks import sync_and_process_emails
    task = sync_and_process_emails.delay()
    return SyncTriggerResponse(
        message="Sincronizacion encolada correctamente",
        task_id=task.id,
    )