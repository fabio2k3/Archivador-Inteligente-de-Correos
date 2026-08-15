import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base


@pytest.fixture
def db_session():
    """
    Crea una base de datos SQLite en memoria, exclusiva para este test.
    Se destruye automaticamente al terminar, sin afectar tu base de datos real.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()