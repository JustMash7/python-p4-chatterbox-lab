import os
import sys
import pytest
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models import db, Message

class TestApp:
    '''Flask application in app.py'''

    @pytest.fixture(autouse=True)
    def setup(self, client, db):
        """Setup and teardown for each test"""
        with client.application.app_context():
            # Clean up any existing test messages
            Message.query.filter(
                Message.body == "Hello 👋",
                Message.username == "Liza"
            ).delete()
            db.session.commit()
            yield

    def test_has_correct_columns(self, client, db):
        '''has correct columns in the Message model.'''
        with client.application.app_context():
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza")
            
            db.session.add(hello_from_liza)
            db.session.commit()

            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

    def test_returns_list_of_json_objects_for_all_messages_in_database(self, client, db):
        '''returns a list of JSON objects for all messages in the database.'''
        with client.application.app_context():
            # Create test messages
            message1 = Message(body="Test message 1", username="Tester")
            message2 = Message(body="Test message 2", username="Tester")
            db.session.add_all([message1, message2])
            db.session.commit()
            
            response = client.get('/messages')
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            
            # Verify response contains our test messages
            messages = response.json
            assert any(m['body'] == "Test message 1" for m in messages)
            assert any(m['body'] == "Test message 2" for m in messages)

    def test_creates_new_message_in_the_database(self, client, db):
        '''creates a new message in the database.'''
        with client.application.app_context():
            response = client.post(
                '/messages',
                json={
                    "body":"Hello 👋",
                    "username":"Liza",
                }
            )
            assert response.status_code == 201
            
            message = Message.query.filter_by(body="Hello 👋").first()
            assert message is not None
            assert message.username == "Liza"

    def test_returns_data_for_newly_created_message_as_json(self, client, db):
        '''returns data for the newly created message as JSON.'''
        with client.application.app_context():
            response = client.post(
                '/messages',
                json={
                    "body":"Hello 👋",
                    "username":"Liza",
                }
            )

            assert response.status_code == 201
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

    def test_updates_body_of_message_in_database(self, client, db):
        '''updates the body of a message in the database.'''
        with client.application.app_context():
            # Create a test message
            test_message = Message(body="Original message", username="Tester")
            db.session.add(test_message)
            db.session.commit()
            
            response = client.patch(
                f'/messages/{test_message.id}',
                json={"body":"Updated message"}
            )
            
            assert response.status_code == 200
            updated = Message.query.get(test_message.id)
            assert updated.body == "Updated message"

    def test_returns_data_for_updated_message_as_json(self, client, db):
        '''returns data for the updated message as JSON.'''
        with client.application.app_context():
            # Create a test message
            test_message = Message(body="Original message", username="Tester")
            db.session.add(test_message)
            db.session.commit()
            
            response = client.patch(
                f'/messages/{test_message.id}',
                json={"body":"Updated message"}
            )
            
            assert response.status_code == 200
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Updated message"

    def test_deletes_message_from_database(self, client, db):
        '''deletes the message from the database.'''
        with client.application.app_context():
            # Create a test message
            test_message = Message(body="Delete me", username="Tester")
            db.session.add(test_message)
            db.session.commit()
            message_id = test_message.id
            
            response = client.delete(f'/messages/{message_id}')
            
            assert response.status_code == 204
            deleted = Message.query.get(message_id)
            assert deleted is None