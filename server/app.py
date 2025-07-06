import os
import sys
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message

def create_app(test_config=None):
    """Application factory function"""
    app = Flask(__name__)
    
    # Configure the app
    if test_config is None:
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI='sqlite:///app.db',
            SQLALCHEMY_TRACK_MODIFICATIONS=False
        )
    else:
        app.config.update(test_config)
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    Migrate(app, db)
    
    @app.route('/messages', methods=['GET'])
    def get_messages():
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([message.to_dict() for message in messages])
    
    @app.route('/messages', methods=['POST'])
    def create_message():
        data = request.get_json()
        if not data or not 'body' in data or not 'username' in data:
            abort(400, description="Invalid request data")
        new_message = Message(body=data['body'], username=data['username'])
        db.session.add(new_message)
        db.session.commit()
        return jsonify(new_message.to_dict()), 201
    
    @app.route('/messages/<int:id>', methods=['PATCH'])
    def update_message(id):
        data = request.get_json()
        message = Message.query.get_or_404(id)
        if 'body' in data:
            message.body = data['body']
        db.session.commit()
        return jsonify(message.to_dict())
    
    @app.route('/messages/<int:id>', methods=['DELETE'])
    def delete_message(id):
        message = Message.query.get_or_404(id)
        db.session.delete(message)
        db.session.commit()
        return '', 204
    
    return app

# Create app instance only when run directly
if __name__ == '__main__':
    app = create_app()
    app.run(port=5555)