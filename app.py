#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from platform import architecture
import sys
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='venue', lazy=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist', lazy=False)


class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    # start_time = db.Column(db.String(), default=datetime.now(), nullable=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    try:
        venues_ = Venue.query.all()
        states = []
        data = []

        if not venues_:
            return render_template('pages/venues.html', areas=[])

        for i in venues_:
            if i.state in states:
                can = states.index(i.state)
                
                data[can]["venues"].append(i)
            else:
                d = {
                    "city": i.city,
                    "state": i.state,
                    "venues": [i]
                }
                states.append(i.state)
                data.append(d)

        return render_template('pages/venues.html', areas=data)
    except:
        flash("Error collecting venues")
        return render_template('pages/venues.html', areas=[])

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    error = False
    try:
        search_term = request.form.get('search_term')
        data = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
        items = []
        for row in data:
            aux = {
            "id": row.id,
            "name": row.name,
            "num_upcoming_shows": len(row.shows)
            }
            items.append(aux)

        response={
            "count": len(items),
            "data": items
        }
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        error = True
    if error == True:
        flash("Error searching please try again later")
        return render_template('pages/venues.html')

def format_venue(Venue):
    d = datetime.utcnow()
    Venue.past_shows = []
    Venue.upcoming_shows = []
    Venue.past_shows_count = 0
    Venue.upcoming_shows_count = 0
    for i in Venue.shows:
        try:
            artist_ = Artist.query.get(i.artist_id)
        except:
            continue
    
        if i.date < d:
            Venue.past_shows.append({
                "artist_id": i.artist_id,
                "artist_name":artist_.name,
                "artist_image_link":artist_.image_link,
                "start_time" : str(i.date)
            })
            Venue.past_shows_count += 1

        elif i.date > d:
            Venue.upcoming_shows.append({
                "artist_id": i.artist_id,
                "artist_name":artist_.name,
                "artist_image_link":artist_.image_link,
                "start_time" : str(i.date)
            })
            Venue.upcoming_shows_count += 1
    return Venue

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # data = Venue.query.filter_by(id=venue_id).first()
    # data.genres = data.genres

    # upcoming_shows = []
    # past_shows = []
    # for show in data.shows:
    #     if show.date > datetime.now():
    #         # show.artist_image_link.append(data.image_link)
    #         upcoming_shows.append(show)
    #     else:
    #         past_shows.append(show)

    # data.upcoming_shows = upcoming_shows
    # data.past_shows = past_shows
    try:
        Ve = Venue.query.get(venue_id)
        if not Ve:
            flash(f"venue with id {venue_id} does not exist")
            return render_template('pages/venues.html', areas=[])

        data = format_venue(Ve)

        venue_com = data.__dict__
        venue_com["genres"] = [venue_com["genres"]]
        return render_template('pages/show_venue.html', venue=venue_com)
    except:
        flash("sorry server currently down, couldn't retrieve venue")
        return render_template('pages/home.html')

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False
    try:
        if request.form.get('seeking_talent') == 'y':
            bol = True
        else:
            bol = False
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        address = request.form.get('address')
        genres = request.form.get('genres')
        website_link = request.form.get('website_link')
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        seeking_talent = bol
        seeking_description = request.form.get('seeking_description')

        venue = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)
        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            abort(400)
        else:
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
            return render_template('pages/home.html')
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
    if error == True:
        db.session.rollback()
        db.session.close()
        flash('Error deleting Venue')
        abort(500)
    else:
        db.session.close()
        flash('Venue Deleted Successfully!')
        return redirect(url_for('venues'))    

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ---------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.order_by('name').all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    data = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
    items = []
    for row in data:
        aux = {
        "id": row.id,
        "name": row.name,
        "num_upcoming_shows": len(row.shows)
        }
        items.append(aux)
    response={
        "count": len(items),
        "data": items
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))



def format_artist(Artist):
    d = datetime.utcnow()
    Artist.past_shows = []
    Artist.upcoming_shows = []
    Artist.past_shows_count = 0
    Artist.upcoming_shows_count = 0
    for i in Artist.shows:
        try:
            artist_ = Artist.query.get(i.artist_id)
        except:
            continue
    
        if i.date < d:
            Artist.past_shows.append({
                "artist_id": i.artist_id,
                "artist_name":artist_.name,
                "artist_image_link":artist_.image_link,
                "start_time" : str(i.date)
            })
            Artist.past_shows_count += 1

        elif i.date > d:
            Artist.upcoming_shows.append({
                "artist_id": i.artist_id,
                "artist_name":artist_.name,
                "artist_image_link":artist_.image_link,
                "start_time" : str(i.date)
            })
            Artist.upcoming_shows_count += 1
    return Artist

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    # data = Artist.query.filter_by(id=artist_id).first()
    # data.genres = data.genres

    # upcoming_shows = []
    # past_shows = []
    # for show in data.shows:
    #     if show.date > datetime.now():
    #         upcoming_shows.append(show)
    #     else:
    #         past_shows.append(show)
    # data.upcoming_shows = upcoming_shows
    # data.past_shows = past_shows
    # return render_template('pages/show_artist.html', artist=data)

    try:
        ar = Venue.query.get(artist_id)
        if not ar:
            flash(f"venue with id {artist_id} does not exist")
            return render_template('pages/venues.html', areas=[])

        data = format_artist(ar)

        artist_ = data.__dict__
        artist_["genres"] = [artist_["genres"]]
        return render_template('pages/show_venue.html', venue=artist_)
    except:
        flash("sorry server currently down, couldn't retrieve artist")
        return render_template('pages/home.html')

    return render_template('pages/show_venue.html', venue=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.filter_by(id=artist_id).first()

    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.facebook_link.data = artist.facebook_link
    form.website_link.data = artist.website_link
    form.image_link.data = artist.image_link
    form.genres.data = artist.genres
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    try:
        if request.form.get('seeking_venue') == 'y':
            bol = True
        else:
            bol = False
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = request.form.get('name')
        artist.city = request.form.get('city')
        artist.state = request.form.get('state')
        artist.phone = request.form.get('phone')
        artist.genres = request.form.get('genres')
        artist.facebook_link = request.form.get('facebook_link')
        artist.website_link = request.form.get('website_link')
        artist.image_link = request.form.get('image_link')
        artist.seeking_venue = bol
        artist.seeking_description = request.form.get('seeking_description')
        
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.filter_by(id=venue_id).first()

    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.facebook_link.data = venue.facebook_link
    form.website_link.data = venue.website_link
    form.image_link.data = venue.image_link
    form.genres.data = venue.genres
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error = False

    try:
        if request.form.get('seeking_talent') == 'y':
            bol = True
        else:
            bol = False

        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.phone = request.form.get('phone')
        venue.genres = request.form.get('genres')
        venue.address = request.form.get('address')
        venue.facebook_link = request.form.get('facebook_link')
        venue.website_link = request.form.get('website_link')
        venue.image_link = request.form.get('image_link')
        venue.seeking_talent = bol
        venue.seeking_description = request.form.get('seeking_description')

        db.session.add(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error = False

    try:
        if request.form.get('seeking_venue') == 'y':
            bol = True
        else:
            bol = False
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.get('genres')
        website_link = request.form.get('website_link')
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        seeking_venue = bol
        seeking_description = request.form.get('seeking_description')

        artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(artist)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if error == True:
            abort(400)
        else:
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
            return render_template('pages/home.html')
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    rows = db.session.query(Show, Artist, Venue).join(Artist).join(Venue).filter().order_by('date').all()
    data = []
    for row in rows:
        item = {
        'venue_id': row.Venue.id,
        'artist_id': row.Artist.id,
        'venue_name': row.Venue.name,
        'artist_name': row.Artist.name,
        'artist_image_link': row.Artist.image_link,
        'start_time': row.Show.date.strftime('%Y-%m-%d %H:%I')
        }
        data.append(item)

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error = False

    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, date=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error == True:
        flash('Invalid venue or artist id!')
        abort(500)
    else:
        flash('Show was successfully listed!')
        return redirect(url_for('shows'))
    # on successful db insert, flash success
    
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
