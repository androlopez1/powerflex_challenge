from sprocket_factory.extensions import db

class Factory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chart_data = db.Column(db.String)

class Sprocket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teeth = db.Column(db.Integer)
    pitch_diameter = db.Column(db.Integer)
    outside_diameter = db.Column(db.Integer)
    pitch = db.Column(db.Integer)