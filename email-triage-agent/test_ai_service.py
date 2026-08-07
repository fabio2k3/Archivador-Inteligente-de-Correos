from app.services.ai_service import analyze_email

result = analyze_email(
    sender="facturacion@electricidad-ejemplo.com",
    subject="Tu factura de luz de Julio ya está disponible",
    body="""Estimado cliente,
    
Tu factura de electricidad correspondiente al mes de Julio ya está disponible.
Monto a pagar: $45.320
Fecha límite de pago: 15 de agosto de 2026

Puedes pagar en línea o en cualquiera de nuestras sucursales autorizadas.
Si no pagas antes de la fecha límite, se aplicará un recargo del 5%.

Gracias por tu preferencia."""
)

print("Resumen:")
for bullet in result["summary_bullets"]:
    print(f"  • {bullet}")
print(f"\nFecha de vencimiento: {result['due_date']}")
print(f"Categoría sugerida: {result['suggested_category']}")