from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(100), nullable=False)
    join_url = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f'<Reuniao {self.topic} - {self.start_time}>'
