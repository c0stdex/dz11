import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from your_module import models, schemas, crud
from your_module.database import Base

class TestCRUD(unittest.TestCase):

    def setUp(self):
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = TestingSessionLocal()

    def tearDown(self):
        self.db.close()

    def test_create_user(self):
        user = schemas.UserCreate(email="test@example.com", password="testpassword")
        created_user = crud.create_user(self.db, user)
        self.assertEqual(created_user.email, "test@example.com")
        self.assertTrue(created_user.hashed_password is not None)

if __name__ == '__main__':
    unittest.main()
