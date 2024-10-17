from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    start_time = db.Column(db.String(255), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    join_url = db.Column(db.String(255), nullable=False)
