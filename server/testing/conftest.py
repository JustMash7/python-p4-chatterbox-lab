import pytest
import os
import sys
import tempfile

# Add parent directory to path to ensure proper imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db as _db

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Create app with test configuration
    app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False
    })
    
    # Create the database and tables
    with app.app_context():
        _db.create_all()
        
    yield app
    
    # Cleanup: close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()

@pytest.fixture
def db(app):
    """Provide database access within tests."""
    with app.app_context():
        yield _db