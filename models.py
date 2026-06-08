from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
db=SQLAlchemy()


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),nullable=False,unique=True)
    email=db.Column(db.String(100),nullable=False,unique=True)
    password=db.Column(db.String(200),nullable=False)
    is_admin=db.Column(db.Boolean,default=False)
    date_joined=db.Column(db.String(50))

class Fighter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    nickname = db.Column(db.String(100))
    nationality = db.Column(db.String(50))
    weight_class = db.Column(db.String(50))
    fighting_style = db.Column(db.String(50))
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    wins_by_ko = db.Column(db.Integer, default=0)
    wins_by_sub = db.Column(db.Integer, default=0)
    wins_by_dec = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    is_nepali = db.Column(db.Boolean, default=False)
    province = db.Column(db.String(100))
    gym = db.Column(db.String(100))
    coach = db.Column(db.String(100))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(300))
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    image = db.Column(db.String(200))
    date_posted = db.Column(db.String(50))
    author = db.Column(db.String(100), default='MMA Dropzone')
    is_published = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)

    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(50))
    event_time = db.Column(db.String(50))
    nepal_time = db.Column(db.String(50))
    venue = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    organization = db.Column(db.String(100))
    main_event = db.Column(db.String(200))
    co_main_event = db.Column(db.String(200))
    description = db.Column(db.Text)
    image = db.Column(db.String(200))
    where_to_watch = db.Column(db.String(200))
    is_completed = db.Column(db.Boolean, default=False)


class Fight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)

    # Fighter 1
    fighter1 = db.Column(db.String(100), nullable=False)
    fighter1_record = db.Column(db.String(20))
    fighter1_id = db.Column(db.Integer, db.ForeignKey('fighter.id'), nullable=True)

    # Fighter 2
    fighter2 = db.Column(db.String(100), nullable=False)
    fighter2_record = db.Column(db.String(20))
    fighter2_id = db.Column(db.Integer, db.ForeignKey('fighter.id'), nullable=True)

    # Fight details
    weight_class = db.Column(db.String(50))
    card_position = db.Column(db.String(50))
    is_title_fight = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)

    # Results
    winner = db.Column(db.String(100))
    winner_id = db.Column(db.Integer, db.ForeignKey('fighter.id'), nullable=True)
    method = db.Column(db.String(50))
    round_finished = db.Column(db.Integer)
    time_finished = db.Column(db.String(10))
    bonus = db.Column(db.String(100))
    is_completed = db.Column(db.Boolean, default=False)

    # Notes
    notes = db.Column(db.Text)

    # Relationships
    event = db.relationship('Event', backref='fights')
    fighter1_obj = db.relationship('Fighter', foreign_keys=[fighter1_id], backref='fights_as_fighter1')
    fighter2_obj = db.relationship('Fighter', foreign_keys=[fighter2_id], backref='fights_as_fighter2')
    winner_obj = db.relationship('Fighter', foreign_keys=[winner_id], backref='fights_won')