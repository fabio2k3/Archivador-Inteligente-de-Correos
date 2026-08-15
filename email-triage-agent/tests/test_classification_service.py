from app.services.classification_service import classify_email, apply_rules


def test_newsletter_con_dos_senales_es_detectado_por_regla():
    resultado = classify_email(
        sender="newsletter@techblog.com",
        subject="Resumen semanal",
        body="Para dejar de recibir estos correos, cancelar suscripcion aqui.",
        ai_suggested_category="importante",  # la IA se equivoca a proposito en el test
    )
    assert resultado["final_category"] == "newsletter"
    assert resultado["decided_by"] == "rule"


def test_newsletter_con_una_sola_senal_no_activa_la_regla():
    # Solo el remitente coincide, falta la señal del cuerpo (unsubscribe)
    resultado = classify_email(
        sender="newsletter@techblog.com",
        subject="Resumen semanal",
        body="Aqui esta el contenido de esta semana, sin nada mas.",
        ai_suggested_category="importante",
    )
    # Como ninguna regla aplico con certeza, debe decidir la IA
    assert resultado["decided_by"] == "ai"
    assert resultado["final_category"] == "importante"


def test_spam_se_detecta_con_una_sola_senal():
    resultado = classify_email(
        sender="premios@ofertas-raras.com",
        subject="Ganaste un premio, haz click urgente",
        body="Reclama tu premio ahora mismo.",
        ai_suggested_category="sin_clasificar",
    )
    assert resultado["final_category"] == "spam"
    assert resultado["decided_by"] == "rule"


def test_correo_ambiguo_sin_reglas_usa_sugerencia_de_ia():
    resultado = classify_email(
        sender="facturacion@electricidad-ejemplo.com",
        subject="Tu factura de luz de Julio",
        body="Fecha limite de pago: 15 de agosto de 2026.",
        ai_suggested_category="importante",
    )
    assert resultado["decided_by"] == "ai"
    assert resultado["final_category"] == "importante"


def test_apply_rules_devuelve_none_cuando_ninguna_regla_aplica():
    resultado = apply_rules(
        sender="colega@miempresa.com",
        subject="Reunion de mañana",
        body="Nos vemos a las 10am para revisar el proyecto.",
    )
    assert resultado is None