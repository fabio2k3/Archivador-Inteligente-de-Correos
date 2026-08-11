from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]

PENDIENTES_LABEL_NAME = "Pendientes"


def get_gmail_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def get_or_create_pendientes_label(service) -> str:
    """
    Busca el label 'Pendientes' en Gmail. Si no existe, lo crea.
    Devuelve el ID del label (Gmail identifica labels por ID, no por nombre).
    """
    labels_response = service.users().labels().list(userId="me").execute()
    labels = labels_response.get("labels", [])

    for label in labels:
        if label["name"] == PENDIENTES_LABEL_NAME:
            return label["id"]

    # No existe, lo creamos
    new_label = service.users().labels().create(
        userId="me",
        body={
            "name": PENDIENTES_LABEL_NAME,
            "labelListVisibility": "labelShow",
            "messageListVisibility": "show",
        }
    ).execute()

    return new_label["id"]


def apply_label_to_message(service, message_id: str, label_id: str) -> None:
    """
    Aplica un label a un mensaje SIN eliminarlo ni tocar otros labels.
    Gmail no 'mueve' mensajes entre carpetas - solo agrega/quita etiquetas.
    """
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"addLabelIds": [label_id]}
    ).execute()