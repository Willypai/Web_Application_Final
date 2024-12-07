from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Reminder {self.id}: {self.content}>'
