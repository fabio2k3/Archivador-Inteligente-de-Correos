from app.db.session import SessionLocal
from app.services.email_orchestrator import process_and_store_email
from test_gmail_auth import get_gmail_service  # reutilizamos la funcion que ya escribimos

def main():
    gmail_service = get_gmail_service()
    db = SessionLocal()

    # Traemos el correo mas reciente de tu bandeja
    results = gmail_service.users().messages().list(userId="me", maxResults=1).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No hay correos.")
        return

    msg_id = messages[0]["id"]
    full_message = gmail_service.users().messages().get(
        userId="me", id=msg_id, format="full"
    ).execute()

    # Revisamos si el correo esta sin leer (Gmail usa la label UNREAD)
    is_unread = "UNREAD" in full_message.get("labelIds", [])

    email_record = process_and_store_email(db, full_message, is_unread)

    print(f"\nCorreo procesado y guardado:")
    print(f"  ID: {email_record.id}")
    print(f"  De: {email_record.sender}")
    print(f"  Asunto: {email_record.subject}")
    print(f"  Categoria: {email_record.category.value}")
    print(f"  Resumen: {email_record.summary}")
    print(f"  Fecha vencimiento: {email_record.due_date}")
    print(f"  Sin leer desde: {email_record.first_seen_unread_at}")

    db.close()

if __name__ == "__main__":
    main()