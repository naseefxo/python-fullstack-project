from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    deadline = db.Column(db.DateTime, nullable=True)
    priority = db.Column(db.String(10), default="Medium")
    category = db.Column(db.String(20), default="General")


    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "deadline": self.deadline.strftime("%Y-%m-%dT%H:%M") if self.deadline else None,
            "priority": self.priority
        }


