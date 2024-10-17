#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config 
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
   __tablename__='shows'   
   id= db.Column(db.Integer,primary_key=True)  
   venue_id= db.Column(db.Integer,db.ForeignKey('venues.id'),nullable=False)  
   artist_id= db.Column(db.Integer,db.ForeignKey('artists.id'),nullable=False)    
   start_time = db.Column(db.DateTime,nullable=True) 
   artists = db.relationship('Artist', backref='show_artist', lazy=True)
   venues = db.relationship('Venue', backref='show_venue', lazy=True)
   
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
    #shows = db.relationship('Show', backref='venues', lazy=True)     
    #past_shows_count= db.Column(db.Integer) 
    #upcoming_shows_count=db.Column(db.Integer)
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

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
    #shows = db.relationship('Show', backref='artists', lazy=True)
 
    #past_shows_count= db.Column(db.Integer,nullable = True)
    #upcoming_shows_count= db.Column(db.Integer,nullable = True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
with app.app_context():
    db.create_all()
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  venues = Venue.query.all()
  for x in venues:
    venue_id = x.id 
    city =  x.city
    state =  x.state
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()
 
  data=[{
    "city": city, #"San Francisco",
    "state": state, #"CA",   
    "venues": [{
        "id": venue.id,#1,
        "name": venue.name,
          #"The Musical Hop",        
        'num_upcoming_shows': len(upcoming_shows)
    }for venue in venues]
  #   {
  #     "id": venues.id#3,
  #     "name":  "Park Square Live Music & Coffee",
  #     "num_upcoming_shows": 1,
  #   }]
  # }, {
  #   "city": "New York",
  #   "state": "NY",
  #   "venues": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
     }]
 
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  query = request.form.get('search_term', '')
   # here the line that filter artist as you want 
  data = Venue.query.filter(Venue.name.ilike(f'%{query}%')).all()
  print(f"Data:{data}")
  searchedVenue = []
  current_time = datetime.now()
  for venue in data:
    count = Show.query.filter_by(venue_id = venue.id).filter(Show.start_time > current_time).count()
    searchedVenue.append({"id":venue.id,"name": venue.name,"num_upcoming_shows":count})
    print(f"searchedVenue:{searchedVenue}")
    response={
      "count": len(data),
      "data": searchedVenue
    }

  response1={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.filter_by(id=venue_id).first_or_404()
  print( venue_id)
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()
  
  # TODO: replace with real venue data from the venues table, using venue_id
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    'past_shows': [{
        'artist_id': artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } 
    for artist, show in past_shows],
    'upcoming_shows': [{
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for artist, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
    }
  
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
 # TODO: insert form data as a new Venue record in the db, instead
  formVenue =VenueForm(request.form,meta={'csrf': False})
  # Validate all fields
  genres_array=[]
  if formVenue.validate():
        try:        
          venue = Venue(name=formVenue.name.data,
          city=formVenue.city.data,
          state=formVenue.state.data,
          address=formVenue.address.data,
          phone=formVenue.phone.data,
          genres_array = genres_array.append({formVenue.genres.data}),          
          genres=genres_array,
          facebook_link=formVenue.facebook_link.data,
          image_link=formVenue.image_link.data,  
          website_link=formVenue.website_link.data,
          seeking_talent=formVenue.seeking_talent.data,
          seeking_description=formVenue.seeking_description.data)

          db.session.add(venue)
          db.session.commit()
          # TODO: modify data to be the data object returned from db insertion
          # on successful db insert, flash success
          
        except ValueError as e:          
          error = True
          db.session.rollback()
          flash('An error occurred. Venue ' + request.form['name']  + ' could not be listed.')
          print(e)
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')
              #abort(400)
          else:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')           
            return render_template('pages/home.html')
  else:
    message = []
    for field, errors in formVenue.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

 
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = Artist.query.all()
  for x in artist:
     id = x.id
     name = x.name
     
  data=[{
    "id": id,
    "name": name}]
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  query = request.form.get('search_term', '')
   # here the line that filter artist as you want 
  data = Artist.query.filter(Artist.name.ilike(f'%{query}%')).all()
  print(f'data: {data}')
  searchedArtists = []
  current_time = datetime.utcnow()
  for artist in data:
    count = Show.query.filter_by(artist_id = artist.id).filter(Show.start_time > current_time).count()
    searchedArtists.append({"id":artist.id,"name": artist.name,"num_upcoming_shows":count})
    response={
      "count": len(data),
      "data": searchedArtists
    }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
   
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  print( artist_id)
  past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).\
    all()

  data={
    "id": artist.id,
    "name": artist.name,#"Guns N Petals",
    "genres": artist.genres, # ["Rock n Roll"],
    "city": artist.city, #"San Francisco",
    "state": artist.state,# "CA",
    "phone": artist.phone,#"326-123-5000",
    "website":artist.website_link, #"https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,#"https://www.facebook.com/GunsNPetals",
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,  #"Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link,# "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    'past_shows': [{
        'venue_id': veneu.id,
        "venue_name": veneu.name,
        "venue_image_link": veneu.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } 
    for veneu, show in past_shows],
    'upcoming_shows': [{
        'venue_id': veneu.id,
        'venue_name': veneu.name,
        'venue_image_link': veneu.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for veneu, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
    }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>  
  artist =  Artist.query.first_or_404(artist_id)
  print(f'artist:{artist}')
  form = ArtistForm(obj=artist) 
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue =  Venue.query.get_or_404(venue_id)
  print(f'venue:{venue}')
  form = VenueForm(obj=venue) 
  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  formVenue =VenueForm(request.form,meta={'csrf': False})
  # Validate all fields
  if formVenue.validate():
        try:           
          venue = Venue.query.get_or_404(venue_id) 
          formVenue.populate_obj(venue)
          db.session.commit()
        except Exception as e:          
          error = True
          db.session.rollback()
          flash('An error occurred. Venue ' + request.form['name']  + ' could not be updated.')
          print(f"Error: {e}")
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')
          else:
            flash('Venue ' + request.form['name'] + ' was successfully updated!')           
            return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    message = []
    for field, errors in formVenue.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    
  
#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  formArtist =ArtistForm(request.form,meta={'csrf': False})
  # Validate all fields
  if formArtist.validate():
        try:           
        # called upon submitting the new artist listing form
          artist = Artist(name=formArtist.name.data,
          city=formArtist.city.data,
          state=formArtist.state.data,          
          phone=formArtist.phone.data,
          genres=formArtist.genres.data,
          facebook_link=formArtist.facebook_link.data,
          image_link=formArtist.image_link.data,  
          website_link=formArtist.website_link.data,
          seeking_venue=formArtist.seeking_venue.data,
          seeking_description=formArtist.seeking_description.data)
          
          db.session.add(artist)
          db.session.commit()
          # TODO: modify data to be the data object returned from db insertion
          # on successful db insert, flash success
          
        except Exception as e:          
          error = True
          db.session.rollback()
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Artist ' + request.form['name']  + ' could not be listed.')
          print(f"Error: {e}")
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')
              #abort(400)
          else:
            # on successful db insert, flash success
            flash('Artist ' + request.form['name'] + ' was successfully listed!')           
            return render_template('pages/home.html')
  else:
    message = []
    for field, errors in formArtist.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
  
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
   
  # displays list of shows at /shows
  shows = db.session.query(Artist, Show).join(Show).join(Venue).all() 
  
  print(f'Shows:{shows}')
  data=[{
     "venue_id":venue.id,
     "venue_name": venue.name,
     "artist_id": show.artists.id,
     "artist_name": show.artists.name,
     "artist_image_link":show.artists.image_link,
       # "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
     "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
  }for venue,show in shows]


  # TODO: replace with real venues data.
  data1=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False
  formShow =ShowForm(request.form,meta={'csrf': False})
  # Validate all fields
  if formShow.validate():
        try: 
        # called upon submitting the new artist listing form
          show = Show(artist_id=formShow.artist_id.data,
          venue_id=formShow.venue_id.data,
          start_time=formShow.start_time.data,          
          )
          db.session.add(show)
          db.session.commit()
          # TODO: modify data to be the data object returned from db insertion
          # on successful db insert, flash success
          
        except Exception as e:          
          error = True
          db.session.rollback()
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Show could not be listed.')
          print(e)
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')
              #abort(400)
          else:
            # on successful db insert, flash success
            flash('Show was successfully listed!')           
            return render_template('pages/home.html')
  else:
    message = []
    for field, errors in formShow.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
    flash('Please fix the following errors: ' + ', '.join(message))
    form = ShowForm()()
    return render_template('forms/new_venue.html', form=form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead 
  

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
