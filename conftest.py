import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.database import get_session
from app.rate_limit import limiter


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def override_dependencies(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    limiter.reset()
    yield
    app.dependency_overrides.clear()