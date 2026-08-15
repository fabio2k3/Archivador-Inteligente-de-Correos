from unittest.mock import patch
from app.services.email_orchestrator import process_and_store_email
from app.db.models import Email


FAKE_GMAIL_MESSAGE = {
    "id": "fake123",
    "threadId": "thread123",
    "snippet": "Este es un correo de prueba",
    "payload": {
        "headers": [
            {"name": "From", "value": "test@ejemplo.com"},
            {"name": "Subject", "value": "Correo de prueba"},
        ]
    },
}

FAKE_AI_RESULT = {
    "summary_bullets": ["Punto 1", "Punto 2", "Punto 3"],
    "due_date": None,
    "suggested_category": "importante",
}


@patch("app.services.email_orchestrator.analyze_email")
def test_correo_nuevo_se_procesa_y_guarda(mock_analyze_email, db_session):
    mock_analyze_email.return_value = FAKE_AI_RESULT

    resultado = process_and_store_email(db_session, FAKE_GMAIL_MESSAGE, is_unread=True)

    assert resultado.gmail_message_id == "fake123"
    assert resultado.category.value == "importante"
    mock_analyze_email.assert_called_once()  # confirma que SI se llamo a la IA


@patch("app.services.email_orchestrator.analyze_email")
def test_correo_existente_no_se_reprocesa(mock_analyze_email, db_session):
    mock_analyze_email.return_value = FAKE_AI_RESULT

    # Primera vez: se procesa normalmente
    process_and_store_email(db_session, FAKE_GMAIL_MESSAGE, is_unread=True)

    # Segunda vez: mismo gmail_message_id, no deberia volver a llamar a la IA
    process_and_store_email(db_session, FAKE_GMAIL_MESSAGE, is_unread=True)

    # Verificamos que analyze_email SOLO se llamo una vez en total, no dos
    mock_analyze_email.assert_called_once()

    # Y que solo existe UN registro en la base de datos, no dos duplicados
    total_correos = db_session.query(Email).count()
    assert total_correos == 1