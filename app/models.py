from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Fabric(db.Model):
    __tablename__ = "fabrics"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )