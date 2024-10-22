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
from sqlalchemy import ForeignKey
from forms import *
import config 
from flask_migrate import Migrate
from datetime import datetime, timedelta
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
# TODO: connect to a local postgresql database
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
   __tablename__='shows'   
   id= db.Column(db.Integer,primary_key=True)  
   venue_id= db.Column(db.Integer,db.ForeignKey('venues.id'),nullable=False)  
   artist_id= db.Column(db.Integer,db.ForeignKey('artists.id'),nullable=False)    
   start_time = db.Column(db.DateTime,nullable=True) 
   artists = db.relationship('Artist', backref='show_artist', lazy=True,cascade='all, delete')
   venues = db.relationship('Venue', backref='show_venue', lazy=True,cascade='all, delete')
   
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
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'
    
class Album(db.Model):
   __tablename__='albums'
   id = db.Column(db.Integer, primary_key=True)
   artist_id= db.Column(db.Integer,db.ForeignKey('artists.id'),nullable=False)     
   album_name =  db.Column(db.String,nullable=True)
   album_cover_link =  db.Column(db.String(500),nullable=True)
   songs = db.Column(db.ARRAY(db.String()),nullable=True)
   artists = db.relationship('Artist', backref='artist_album', lazy=True ,cascade='all, delete')

   def __repr__(self):
      return f'<Song {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
with app.app_context():
    db.create_all()




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
  for venue in venues:
    venue_id = venue.id 
    city =  venue.city
    state = venue.state
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  upcoming_shows = db.session.query(Artist).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time > datetime.now()
    ).\
    all()
 
  data=[{
    "city": city, 
    "state": state,   
    "venues": [{
        "id": venue.id,
        "name": venue.name,                
        'num_upcoming_shows': len(upcoming_shows)
    }for venue in venues]
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
  past_shows = db.session.query(Artist).join(Show).join(Venue).\
    filter(
        Show.venue_id == venue_id,
        Show.artist_id == Artist.id,
        Show.start_time < datetime.now()
    ).\
    all()
  
  upcoming_shows = db.session.query(Artist).join(Show).join(Venue).\
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
  if formVenue.validate():
        try: # TODO: modify data to be the data object returned from db insertion        
          venue = Venue(name=formVenue.name.data,
          city=formVenue.city.data,
          state=formVenue.state.data,
          address=formVenue.address.data,
          phone=formVenue.phone.data,
          genres=formVenue.genres.data,
          facebook_link=formVenue.facebook_link.data,
          image_link=formVenue.image_link.data,  
          website_link=formVenue.website_link.data,
          seeking_talent=formVenue.seeking_talent.data,
          seeking_description=formVenue.seeking_description.data)
          db.session.add(venue)
          db.session.commit() 
        except ValueError as e:          
          error = True
          db.session.rollback()
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Venue ' + request.form['name']  + ' could not be listed.')
          print(e)
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')              
          else:  
            # on successful db insert, flash success      
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
  

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter_by(id=venue_id).first_or_404()
        db.session.delete(venue)
        db.session.commit()
        flash("Venue " + request.form['name'] + " is deleted successfully!")
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        flash("Venue " + request.form['name'] + " could not be deleted.")
    finally:
        db.session.close()
    return None
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
   

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()     
  data=[{
    "id": artist.id,
    "name": artist.name
    }for artist in artists] 
  
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
  
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
   
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.filter_by(id=artist_id).first_or_404()
  print( artist_id)
  albums = db.session.query(Artist, Album).filter_by(id=artist_id).all()
  past_shows = db.session.query(Artist).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time < datetime.now()
    ).\
    all()
  print( past_shows)
  upcoming_shows = db.session.query(Artist).join(Show).join(Venue).\
    filter(
        Show.venue_id == Venue.id,
        Show.artist_id == artist_id,
        Show.start_time > datetime.now()
    ).\
    all()
  print( upcoming_shows)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres, 
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website":artist.website_link, 
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,  
    "image_link": artist.image_link,
    'past_shows': [{
        'venue_id': show.venues.id,
        "venue_name":show.venues.name,
        "venue_image_link": show.venues.image_link,
        "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
    } 
    for venue, show in past_shows],
    'upcoming_shows': [{
        'venue_id': show.venues.id,
        'venue_name': show.venues.name,
        'venue_image_link': show.venues.image_link,
        'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M")
    } for veneu, show in upcoming_shows],
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows),
    'song_album': [{
        'artist_id': album.artists.id,
        "artist_name":album.artists.name,
        "album_name": album.album_name,
        "album_cover_link": album.album_cover_link,
        "songs": album.songs
    } for artist, album in albums],
        "past_albums_count":len(albums)
    }
  print(f'Data: {data}')
  data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>  
  artist = Artist.query.get_or_404(artist_id)
  print(f'artist:{artist}')
  form = ArtistForm(obj=artist) 
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  formArtist =ArtistForm(request.form,meta={'csrf': False})
  # Validate all fields
  if formArtist.validate():
        try:           
          artist = Artist.query.get_or_404(artist_id) 
          formArtist.populate_obj(artist)
          db.session.commit()
        except Exception as e:          
          error = True
          db.session.rollback()
          flash('An error occurred. Artist ' + request.form['name']  + ' could not be updated.')
          print(f"Error: {e}")
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')
          else:
            flash('Venue ' + request.form['name'] + ' was successfully updated!')           
            return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    message = []
    for field, errors in formArtist.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
# TODO: populate form with values from venue with ID <venue_id>
  venue =  Venue.query.get_or_404(venue_id)
  print(f'venue:{venue}')
  form = VenueForm(obj=venue) 
  
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
        try:# TODO: modify data to be the data object returned from db insertion
          # on successful db insert, flash success           
        # called upon submitting the new artist listing form
          artist = Artist(name=formArtist.name.data,
          city=formArtist.city.data,
          state=formArtist.state.data,          
          phone=formArtist.phone.data,
          genres=formArtist.genres.data,
          facebook_link= formArtist.facebook_link.data,
          image_link=formArtist.image_link.data,  
          website_link=formArtist.website_link.data,
          seeking_venue=formArtist.seeking_venue.data,
          seeking_description=formArtist.seeking_description.data)
          db.session.add(artist)
          db.session.commit()
          
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
  shows = db.session.query(Artist).join(Show).join(Venue).all() 
  
  print(f'Shows:{shows}')
  data=[{
     "venue_id":show.venues.id,
     "venue_name": show.venues.name,
     "artist_id": show.artists.id,
     "artist_name": show.artists.name,
     "artist_image_link":show.artists.image_link,
       # "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
     "start_time": show.start_time.strftime("%m/%d/%Y, %H:%M")
  }for venue,show in shows]
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
  book_time_valid = Show.query.filter_by(artist_id = formShow.artist_id.data).filter(formShow.start_time.data < Show.start_time).all()
  print(f'Time Query1: {book_time_valid}')
  count = len(book_time_valid)
   
  # Validate all fields
  if count == 0 :
    if formShow.validate():
          try:  # TODO: modify data to be the data object returned from db insertion
          # called upon submitting the new artist listing form
            show = Show(artist_id=formShow.artist_id.data,
            venue_id=formShow.venue_id.data,
            start_time=formShow.start_time.data,          
            )
            db.session.add(show)
            db.session.commit()
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
      flash('Please fix the following errors: ' + ', '.join(message))
      form = ShowForm()
      return render_template('forms/new_show.html', form=form)
  else:     
    flash('Show was unsuccessfully listed! Start time ' + request.form['start_time']+' is not available!') 
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)
  
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead 
  

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/albums/create', methods=['GET'])
def create_ambum_form():
  form = AlbumForm()
  return render_template('forms/new_album.html', form=form)

@app.route('/albums/create', methods=['POST'])
def create_album_submission():
  error = False
 # TODO: insert form data as a new Venue record in the db, instead
  formAlbum =AlbumForm(request.form,meta={'csrf': False})
  
  song_list =formAlbum.song_names.data
  songs = song_list.split(' ')
 # Validate all fields
  if formAlbum.validate():
        try: # TODO: modify data to be the data object returned from db insertion     
          album= Album(artist_id =formAlbum.artist_id.data,
                       album_name = formAlbum.album_name.data,
                       album_cover_link = formAlbum.album_cover_link.data,
                       songs =songs )          
          
          db.session.add(album)
          db.session.commit()
        except ValueError as e:          
          error = True
          db.session.rollback()
          # TODO: on unsuccessful db insert, flash an error instead.
          flash('An error occurred. Album ' + request.form['album_name']  + ' could not be listed.')
          print(e)
        finally:
          db.session.close()           
          if  error == True:
              return render_template('errors/500.html')              
          else:  
            # on successful db insert, flash success      
            flash('Album ' + request.form['album_name'] + ' was successfully listed!')           
            return render_template('pages/home.html')
  else:
    message = []
    for field, errors in formAlbum.errors.items():
        for error in errors:
            message.append(f"{field}: {error}")
    flash('Please fix the following errors: ' + ', '.join(message))
    form = AlbumForm()()
    return render_template('forms/new_album.html', form=form)



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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
