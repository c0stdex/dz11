from fastapi.testclient import TestClient
from your_module.main import app
from your_module.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
