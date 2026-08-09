from app.services.classification_service import classify_email

casos = [
    {
        "nombre": "Newsletter obvio (debe ganar la regla)",
        "sender": "newsletter@techblog.com",
        "subject": "Tu resumen semanal de noticias",
        "body": "Aqui tienes las noticias de la semana. Para dejar de recibir estos correos, cancelar suscripcion aqui.",
        "ai_suggested_category": "importante",  # simulamos que la IA se equivoco
    },
    {
        "nombre": "Factura importante (debe ganar la IA, sin reglas)",
        "sender": "facturacion@electricidad-ejemplo.com",
        "subject": "Tu factura de luz de Julio",
        "body": "Fecha limite de pago: 15 de agosto de 2026.",
        "ai_suggested_category": "importante",
    },
    {
        "nombre": "Spam obvio (debe ganar la regla)",
        "sender": "premios@ofertas-raras.com",
        "subject": "Ganaste un premio, haz click urgente",
        "body": "Reclama tu premio ahora mismo.",
        "ai_suggested_category": "sin_clasificar",
    },
]

for caso in casos:
    resultado = classify_email(
        sender=caso["sender"],
        subject=caso["subject"],
        body=caso["body"],
        ai_suggested_category=caso["ai_suggested_category"],
    )
    print(f"{caso['nombre']}")
    print(f"  Categoria final: {resultado['final_category']} (decidido por: {resultado['decided_by']})")
    print("-" * 60)