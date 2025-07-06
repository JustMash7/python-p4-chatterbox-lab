import os
import sys
import pytest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, Message

class TestMessage:
    '''Message model in models.py'''

    @pytest.fixture(autouse=True)
    def setup(self, app):
        """Setup and teardown for each test"""
        with app.app_context():
            # Clean up any existing test messages
            Message.query.filter(
                Message.body == "Hello 👋",
                Message.username == "Liza"
            ).delete()
            db.session.commit()
            yield

    def test_has_correct_columns(self, app):
        '''has columns for message body, username, and creation time.'''
        with app.app_context():
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

    def test_required_fields(self, app):
        '''requires body and username.'''
        with app.app_context():
            # Test missing body
            with pytest.raises(Exception):
                message = Message(username="Tester")
                db.session.add(message)
                db.session.commit()
            
            # Test missing username
            with pytest.raises(Exception):
                message = Message(body="Test message")
                db.session.add(message)
                db.session.commit()

    def test_timestamps(self, app):
        '''has automatically populated created_at and updated_at fields.'''
        with app.app_context():
            message = Message(body="Test message", username="Tester")
            db.session.add(message)
            db.session.commit()
            
            assert message.created_at is not None
            assert message.updated_at is not None
            original_updated_at = message.updated_at
            
            # Test updated_at changes on update
            message.body = "Updated message"
            db.session.commit()
            assert message.updated_at > original_updated_at