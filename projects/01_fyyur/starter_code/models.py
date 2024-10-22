
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Show(db.Model):
   __tablename__='shows'   
   id= db.Column(db.Integer,primary_key=True)  
   venue_id= db.Column(db.Integer,db.ForeignKey('venues.id'),nullable=False)  
   artist_id= db.Column(db.Integer,db.ForeignKey('artists.id'),nullable=False)    
   start_time = db.Column(db.DateTime,nullable=True) 
   #artists = db.relationship('Artist', backref='show_artist', lazy='joined',cascade='all, delete')
   #venues = db.relationship('Venue', backref='show_venue', lazy='joined',cascade='all, delete')
   
   def __repr__(self):
      return f'<Show {self.id} {self.venue_id} {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'venues'
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String(),nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    address = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_talent=db.Column(db.Boolean,nullable=False,default = False)
    seeking_description =  db.Column(db.String(500),nullable=False)
    shows = db.relationship('Show', backref='venue', lazy='joined',cascade='all, delete')
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a db migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'
    id = db.Column(db.Integer, primary_key=True)    
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120),nullable=False)
    genres = db.Column(db.ARRAY(db.String()),nullable=False)
    image_link = db.Column(db.String(500),nullable=False)
    facebook_link = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120),nullable=False)
    seeking_venue= db.Column(db.Boolean, default=False)
    seeking_description=db.Column(db.String(500),nullable=False)
    shows = db.relationship('Show', backref='artist', lazy='joined',cascade='all, delete')
    #albums =   db.relationship('Album', backref='artist_album', lazy='joined',cascade='all, delete')
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
    
class Album(db.Model):
   __tablename__='albums'
   id = db.Column(db.Integer, primary_key=True)
   artist_id= db.Column(db.Integer,db.ForeignKey('artists.id'),nullable=False)     
   album_name =  db.Column(db.String,nullable=True)
   album_cover_link =  db.Column(db.String(500),nullable=True)
   songs = db.Column(db.ARRAY(db.String()),nullable=True)
   artists = db.relationship('Artist', backref='album', lazy='joined' ,cascade='all, delete')

   def __repr__(self):
      return f'<Song {self.id} {self.name}>'