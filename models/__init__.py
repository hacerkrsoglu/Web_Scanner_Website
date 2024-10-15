# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()  # db burada tanımlanır

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)  # Şifre alanı eklendi

    scans = db.relationship('Scan', backref='user', lazy=True)  # Kullanıcı ile taramalar arasında ilişki

class Scan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Scan {self.url}>'
