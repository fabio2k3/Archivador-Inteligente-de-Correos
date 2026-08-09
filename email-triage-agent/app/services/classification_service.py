NEWSLETTER_SENDER_PATTERNS = [
    "newsletter@", "noreply@", "no-reply@", "notifications@", "news@",
]

NEWSLETTER_BODY_KEYWORDS = [
    "darse de baja", "unsubscribe", "cancelar suscripcion",
    "gestionar preferencias", "manage preferences",
]

SPAM_KEYWORDS = [
    "ganaste un premio", "haz click aqui urgente", "lottery winner",
    "cuenta bloqueada haz click", "verifica tu cuenta ahora",
]


def apply_rules(sender: str, subject: str, body: str) -> str | None:
    """
    Aplica reglas deterministas. Devuelve una categoria si alguna regla
    coincide con certeza razonable, o None si ninguna aplica (dejando
    que decida la IA).
    """
    sender_lower = sender.lower()
    subject_lower = subject.lower()
    body_lower = body.lower()

    # Regla de spam: cualquier coincidencia es suficientemente sospechosa
    for keyword in SPAM_KEYWORDS:
        if keyword in subject_lower or keyword in body_lower:
            return "spam"

    # Regla de newsletter: requerimos DOS señales, no una sola
    sender_matches_newsletter = any(p in sender_lower for p in NEWSLETTER_SENDER_PATTERNS)
    body_has_unsubscribe = any(k in body_lower for k in NEWSLETTER_BODY_KEYWORDS)

    if sender_matches_newsletter and body_has_unsubscribe:
        return "newsletter"

    return None  # ninguna regla aplico con certeza


def classify_email(sender: str, subject: str, body: str, ai_suggested_category: str) -> dict:
    """
    Combina reglas deterministas con la sugerencia de la IA.
    Las reglas tienen prioridad cuando aplican (mas confiables y gratis).
    Si ninguna regla aplica, se usa la sugerencia de la IA.
    """
    rule_result = apply_rules(sender, subject, body)

    if rule_result is not None:
        return {
            "final_category": rule_result,
            "decided_by": "rule",
        }

    return {
        "final_category": ai_suggested_category,
        "decided_by": "ai",
    }