from sqlalchemy import inspect
from app.db.session import engine

inspector = inspect(engine)
columns = inspector.get_columns("emails")

print("Columnas de la tabla 'emails':\n")
for col in columns:
    print(f"  {col['name']:<25} {col['type']}")