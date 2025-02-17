from imports import *
# Table containing user data


class user_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    surname = db.Column(db.String(200), nullable=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    public_id = db.Column(db.String(50), unique=True, nullable=False)
    def __repr__(self):
        return '<Task %r>' % self.id

    def __init__(self, name, surname, username, password, public_id,email, is_admin):
        self.name = name
        self.surname = surname
        self.username = username
        self.password = password
        self.email = email
        self.public_id = public_id
        self.is_admin = is_admin

    def serialize(self):
        return {
            'name': self.name,
            'surname': self.surname,
            'username': self.username,
            'email': self.email,
            'public_id': self.public_id,
            'is_admin' : self.is_admin,
            'date_created': str(self.date_created)
        }

# Table containing followers and following users
#show theatre class
class Theatre(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    #theatre_id = db.Column(db.Integer, primary_key=True)
    theatrename = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    showings = db.relationship('Showing', backref='theatre', lazy=True)

    def __init__(self, theatrename, location, capacity):
        self.theatrename = theatrename
        self.location = location
        self.capacity = capacity

    def serialize(self):
        return {
            'id': self.id,
            'theatrename': self.theatrename,
            'location': self.location,
            'capacity': self.capacity,
            'date_created': self.date_created,
        }

show_theatre = db.Table('show_theatre',
                        db.Column('show_id', db.Integer, db.ForeignKey('show.id'), primary_key=True),
                        db.Column('theatre_id', db.Integer, db.ForeignKey('theatre.id'), primary_key=True)
                        )

class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    showname = db.Column(db.String(100), nullable=False)
    time = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    tag = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    showings = db.relationship('Showing', backref='show', lazy=True)

    def __init__(self, showname, time, rating, price, tag):
        self.showname = showname
        self.time = time
        self.rating = rating
        self.price = price
        self.tag = tag

    def serialize(self):
        return {
            'id': self.id,
            'showname': self.showname,
            'time': self.time,
            'rating': self.rating,
            'price': self.price,
            'tag': self.tag,
            'date_created': self.date_created,
        }

class Showing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'))
    theatre_id = db.Column(db.Integer, db.ForeignKey('theatre.id'))
    available = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='showing', lazy=True)

    def __init__(self, show_id, theatre_id, available):
        self.show_id = show_id
        self.theatre_id = theatre_id
        self.available = available

    def serialize(self):
        return {
            'id': self.id,
            'show_id': self.show_id,
            'theatre_id': self.theatre_id,
            'available': self.available,
            'date_created': self.date_created,
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user_data.id'), nullable=False)
    showing_id = db.Column(db.Integer, db.ForeignKey('showing.id'), nullable=False)
    num_seats = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, user_id, showing_id, num_seats):
        self.user_id = user_id
        self.showing_id = showing_id
        self.num_seats = num_seats

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'showing_id': self.showing_id,
            'num_seats': self.num_seats,
            'date_created': self.date_created,
        }




# Decorator for token verification

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if request.headers.get('x-access-token'):
            token = request.headers['x-access-token']
        if not token:
            return make_response(jsonify({'message': 'Token is missing!'}), 401)
        try:
            data = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = user_data.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return make_response(jsonify({'message': 'Token is invalid!'}), 401)
        return f(current_user, *args, **kwargs)
    return decorated



# With every request, check if token is valid
class verify_token(Resource):

    method_decorators = [token_required]

    def get(self, current_user):
        return make_response(jsonify({'message': 'Token verified successfully!', 'status': 'success'}), 200)

api.add_resource(verify_token, '/api/verify_token')

# Check if API is working with each template render
class apiCheck(Resource):

    # Check API
    def get(self):
        return make_response(jsonify({'status': 'Success'}), 200)

api.add_resource(apiCheck, '/apiCheck')


# Register new user
class Register(Resource):

    # Register a new user
    def post(self):
        data = request.json
        # match user by username or email
        user = user_data.query.filter_by(username=data['username']).first()
        try:
            if user:
                return make_response(jsonify({'message': 'User already exists', 'status': 'error'}), 409)
            else:
                hashed_password = generate_password_hash(
                    data['password'], method='sha256')
                new_user = user_data(name=data['name'], surname=data['surname'], username=data['username'], password=hashed_password,
                                     public_id=str(uuid.uuid4()), email=data['email'],is_admin=False,)
                db.session.add(new_user)
                db.session.commit()
                return make_response(jsonify({'message': 'Registered successfully!', 'status': 'success'}), 201)
        except:
            return make_response(jsonify({'message': 'Error!', 'status': 'error'}), 400)

api.add_resource(Register, '/api/register')

# Login and return JWT token
class Login(Resource):

    # Login a user and obtain JWT token
    def post(self):
        auth = request.json
        username = auth['username']
        password = auth['password']
        print(username,password)
        if not username or not password:
            return make_response(jsonify({'message': 'Please enter all fields!', 'status': 'error'}), 401)
        user = user_data.query.filter_by(username=username).first()
        if not user:
            return make_response(jsonify({'message': 'User does not exist!', 'status': 'error'}), 404)
        if check_password_hash(user.password, password):
            #expiration_time = datetime.utcnow() + timedelta(days=36500)
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
            ) + timedelta(days=36500)}, app.config['SECRET_KEY'], algorithm="HS256")
            return make_response(jsonify({'token': token, 'user_data': user.serialize(), 'status': 'success'}), 200)
        return make_response(jsonify({'message': 'Incorrect password!', 'status': 'error'}), 401)

api.add_resource(Login, '/api/login')

def check_password(a,b):
    if a==b:
        return True
    return False

class AdminLogin(Resource):

    # Login a user and obtain JWT token
    def post(self):
        auth = request.json
        username = auth['username']
        password = auth['password']
        if not username or not password:
            return make_response(jsonify({'message': 'Please enter all fields!', 'status': 'error'}), 401)
        user = user_data.query.filter_by(username=username).first()
        if not user:
            return make_response(jsonify({'message': 'User does not exist!', 'status': 'error'}), 404)
        if check_password(user.password, password) and (user.is_admin==True):
            token = jwt.encode({'public_id': user.public_id, 'exp': datetime.utcnow(
            ) + timedelta(days=36500)}, app.config['SECRET_KEY'], algorithm="HS256")
            return make_response(jsonify({'token': token, 'user_data': user.serialize(), 'status': 'success'}), 200)
        return make_response(jsonify({'message': 'Incorrect password!', 'status': 'error'}), 401)

api.add_resource(AdminLogin, '/api/adminlogin')


#fetching all theatres
class Theatres(Resource):
    def get(self):
        theatres = Theatre.query.order_by(Theatre.date_created.desc()).all()
        theatre_list = []
        for theatre in theatres:
            theatre_data = {
                'id': theatre.id,
                'theatrename': theatre.theatrename,
                'location': theatre.location,
                'capacity': theatre.capacity
            }
            theatre_list.append(theatre_data)
        return jsonify({'status': 'success', 'theatres': theatre_list})


api.add_resource(Theatres, '/api/theatres')

#fetching all shows
class Shows(Resource):
    def get(self):
        shows = Show.query.order_by(Show.date_created.desc()).all()
        show_list = []
        for show in shows:
            show_data = {
                'id': show.id,
                'showname': show.showname,
                'time': show.time,
                'rating': show.rating,
                'price': show.price,
                'tag': show.tag
            }
            show_list.append(show_data)
        return jsonify({'status': 'success', 'shows': show_list})


api.add_resource(Shows, '/api/shows')
 
class fetch_theatre(Resource):

    method_decorators = [token_required]
    @cache.cached(timeout=120)
    def get(self, current_user, theatre_id):
        theatre = Theatre.query.filter_by(id=theatre_id).first()
        if theatre is None:
            return make_response(jsonify({'message': 'Theatre not found!'}), 404)
        theatre_details = {
            'theatrename': theatre.theatrename,
            'location': theatre.location,
            'capacity': theatre.capacity
        }
        return make_response(jsonify({'theatre': theatre_details, 'status': 'success'}), 200)

api.add_resource(fetch_theatre, '/api/fetch_theatre/<theatre_id>')


class ShowsForTheatre(Resource):
    @cache.cached(timeout=120)
    def get(self, theatre_id):
        #shows = Showing.query.filter_by(theatre_id=theatre_id).all()
        shows = Showing.query.filter_by(theatre_id=theatre_id).order_by(Showing.date_created.desc()).all()

        show_list = []
        for showing in shows:
            show = showing.show
            show_data = {
                'showing_id': showing.id,
                'id': show.id,
                'showname': show.showname,
                'time': show.time,
                'rating': show.rating,
                'price': show.price,
                'tag': show.tag,
                'available': showing.available
            }
            show_list.append(show_data)
        return make_response(jsonify({'status': 'success', 'shows': show_list}))
api.add_resource(ShowsForTheatre, '/api/shows/theatre/<theatre_id>')


# e API resource class for booking a show
class BookShow(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.get_json()

        showing_id = data.get('showing_id')
        num_seats = data.get('num_seats')
        showing = Showing.query.filter_by(id=showing_id).first()

        if not showing_id or not num_seats:
            return make_response(jsonify({'message': 'Invalid request. Both showing_id and num_seats are required.'}), 400)

        if showing.available < num_seats:
            return make_response(jsonify({'message': 'Not enough seats available for this show.'}), 400)

        showing.available -= num_seats

        ticket = Booking(showing_id=showing.id, user_id=current_user.id, num_seats=num_seats)
        db.session.add(ticket)
        db.session.commit()

        theater_name = showing.theatre.theatrename
        show_name = showing.show.showname

        return make_response(jsonify({
            'message': 'Booking successful!',
            'theater_name': theater_name,
            'show_name': show_name
        }), 200)

api.add_resource(BookShow, '/api/book_show')




class UserBookings(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        user_id = current_user.id
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.date_created.desc()).all()
        print(user_id,bookings)
        booked_tickets = []

        for booking in bookings:
            ticket_details = {
                'id': booking.id,
                'user_id': booking.user_id,
                'showing_id': booking.showing_id,
                'num_seats': booking.num_seats,
                'date_created': booking.date_created
            }

            # Fetch show details
            show_details = {
                'showname': booking.showing.show.showname,
                'time': booking.showing.show.time,
                'rating': booking.showing.show.rating,
                'price': booking.showing.show.price,
                'tag': booking.showing.show.tag,
                'date_created': booking.showing.show.date_created
            }

            # Fetch theatre details
            theatre_details = {
                'theatrename': booking.showing.theatre.theatrename,
                'location': booking.showing.theatre.location,
                'capacity': booking.showing.theatre.capacity,
                'date_created': booking.showing.theatre.date_created
            }

            ticket_details['show_details'] = show_details
            ticket_details['theatre_details'] = theatre_details

            booked_tickets.append(ticket_details)

        return jsonify({'booked_tickets': booked_tickets, 'message': 'success'})
api.add_resource(UserBookings, '/api/user_bookings')

#resource class for creating new shows
class createShow(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.form.to_dict()
        #data = request.json
        print(data)
        # Parse the time data
        try:
            time_str = data['time']
            time = datetime.strptime(time_str, "%H:%M")
        except:
            return make_response(jsonify({'message': 'Invalid time format. Please provide time in HH:MM format.', 'status': 'error'}), 400)
        
        show = Show(
            showname=data['showname'],
            time=time.strftime("%H:%M"),
            rating=float(data['rating']),
            price=int(data['price']),
            tag=data['tag']
        )
        db.session.add(show)
        db.session.commit()

        #selected_theatres = request.form.getlist('theatres')
        selected_theatres = data['theatres']
        selected_theatres = json.loads(selected_theatres)
        print(type(selected_theatres))


        theatres = Theatre.query.filter(Theatre.id.in_(selected_theatres)).all()
        print(theatres)
        for theatre in theatres:
            print(theatre)
            showing = Showing(show_id=show.id, theatre_id=theatre.id, available=theatre.capacity)
            db.session.add(showing)
        
        db.session.commit()

        return make_response(jsonify({'message': 'Show created successfully!', 'status': 'success'}), 200)

api.add_resource(createShow, '/api/create_show')

#creating new theatres 
class createTheatre(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.form.to_dict()
        theatre = Theatre(
            theatrename=data['theatrename'],
            location=data['location'],
            capacity=int(data['capacity'])
        )
        db.session.add(theatre)
        db.session.commit()

        return make_response(jsonify({'message': 'Theatre created successfully!', 'status': 'success'}), 200)

api.add_resource(createTheatre, '/api/create_theatre')


class EditTheatre(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.json
        theatre_id = data.get('theatre_id')
        theatre = Theatre.query.filter_by(id=theatre_id).first()

        if theatre is None:
            return make_response(jsonify({'message': 'theatre not found!'}), 404)

        if not current_user.is_admin :
            return make_response(jsonify({'message': 'You are not authorized to edit this theatre!'}), 401)

        theatre.theatrename = data.get('theatrename', theatre.theatrename)
        theatre.location = data.get('location', theatre.location)
        theatre.capacity = data.get('capacity', theatre.capacity)

        try:
            db.session.commit()
            return make_response(jsonify({'message': "theatre updated", 'status': 'success'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)

api.add_resource(EditTheatre, '/api/edit_theatre')

class EditShow(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        print('post')
        data = request.json
        print(data)

        show_id = data.get('show_id')
        print(show_id)
        show = Show.query.filter_by(id=show_id).first()

        if show is None:
            return make_response(jsonify({'message': 'Show not found!'}), 404)

        if not current_user.is_admin :
            return make_response(jsonify({'message': 'You are not authorized to edit this show!'}), 401)

        # Parse the time data
        if 'time' in data:
            try:
                time_str = data['time']
                time = datetime.strptime(time_str, "%H:%M")
                show.time = time.strftime("%H:%M")
            except ValueError:
                return make_response(jsonify({'message': 'Invalid time format. Please provide time in HH:MM format.', 'status': 'error'}), 400)

        # Update show attributes based on the data received from the request
        show.showname = data.get('showname', show.showname)
        show.rating = float(data.get('rating', show.rating))
        show.price = int(data.get('price', show.price))
        show.tag = data.get('tag', show.tag)

        # Get the selected theaters and update the showings
        selected_theatres = request.form.getlist('theatres')
        theatres = Theatre.query.filter(Theatre.id.in_(selected_theatres)).all()

        # Update the associated showings
        show.showings = []
        for theatre in theatres:
            showing = Showing(show_id=show.id, theatre_id=theatre.id, available=theatre.capacity)
            show.showings.append(showing)

        try:
            db.session.commit()
            return make_response(jsonify({'message': "Show updated", 'status': 'success'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)

api.add_resource(EditShow, '/api/edit_show')


#delete 

class DeleteTheatre(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.json
        theatre_id = data.get('theatre_id')
        theatre = Theatre.query.filter_by(id=theatre_id).first()

        if theatre is None:
            return make_response(jsonify({'message': 'Theatre not found!'}), 404)

        if not current_user.is_admin :
            return make_response(jsonify({'message': 'You are not authorized to delete this theatre!'}), 401)

        try:
            db.session.delete(theatre)
            db.session.commit()
            redis_client.delete(current_user.username)
            return make_response(jsonify({'message': 'Theatre deleted', 'status': 'success'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)

api.add_resource(DeleteTheatre, '/api/delete_theatre')

class DeleteShow(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.json
        show_id = data.get('show_id')
        show = Show.query.filter_by(id=show_id).first()

        if show is None:
            return make_response(jsonify({'message': 'Show not found!'}), 404)

        if not current_user.is_admin :
            return make_response(jsonify({'message': 'You are not authorized to delete this show!'}), 401)

        try:
            db.session.delete(show)
            db.session.commit()
            redis_client.delete(current_user.username)
            return make_response(jsonify({'message': 'Show deleted', 'status': 'success'}), 200)
        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({'message': str(e)}), 500)

api.add_resource(DeleteShow, '/api/delete_show')



@celery.task
def reminder(bind=True):
    users = user_data.query.all()
    for user in users:
        book_data = Booking.query.filter_by(user_id=user.id).filter(extract('day', Booking.date_created) == datetime.now().day).all()
        if len(book_data) == 0:
            no_booking_template =  render_template('no_booking.html', name=user.name)
            send_email(user.email, "You're missing the movies!!!", no_booking_template)

    return None



from flask import render_template_string

@celery.task(bind=True)
def monthly_report():
    users = user_data.query.all()

    for user in users:
        bookings = Booking.query.filter_by(user_id=user.id).filter(
            extract('month', Booking.date_created) == datetime.now().month
        ).all()

        shows_seen = len(bookings)
        total_ratings = 0

        for booking in bookings:
            total_ratings += booking.show.rating

        if shows_seen > 0:
            average_rating = total_ratings / shows_seen
        else:
            average_rating = 0

        data = {
            'user': user,
            'bookings_made': len(bookings),
            'shows_seen': shows_seen,
            'average_rating': average_rating,
        }

        monthly_report_template = render_template_string(open('monthly_report_template.html').read(), data=data)

        send_email(user.email, "Monthly Report", monthly_report_template)

    return None



class TheatreCSV(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        user_id = current_user.id
        showing = Showing.query.filter_by(user_id=user_id).order_by(Booking.date_created.desc()).all()
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.date_created.desc()).all()
        print(user_id,bookings)
        booked_tickets = []

        for booking in bookings:
            ticket_details = {
                'id': booking.id,
                'user_id': booking.user_id,
                'showing_id': booking.showing_id,
                'num_seats': booking.num_seats,
                'date_created': booking.date_created
            }

            # Fetch show details
            show_details = {
                'showname': booking.showing.show.showname,
                'time': booking.showing.show.time,
                'rating': booking.showing.show.rating,
                'price': booking.showing.show.price,
                'tag': booking.showing.show.tag,
                'date_created': booking.showing.show.date_created
            }

            # Fetch theatre details
            theatre_details = {
                'theatrename': booking.showing.theatre.theatrename,
                'location': booking.showing.theatre.location,
                'capacity': booking.showing.theatre.capacity,
                'date_created': booking.showing.theatre.date_created
            }

            ticket_details['show_details'] = show_details
            ticket_details['theatre_details'] = theatre_details

            booked_tickets.append(ticket_details)

        return jsonify({'booked_tickets': booked_tickets, 'message': 'success'})
api.add_resource(TheatreCSV, '/api/TheatreCSV')




def export_theatre_details(theatre):
    theatre_details = theatre.serialize()

    # Get Number of Shows
    num_shows = len(theatre.showings)

    # Get Bookings and Available Seats
    bookings = Booking.query.join(Showing, Showing.id == Booking.showing_id)\
                            .filter(Showing.theatre_id == theatre_details['id'])\
                            .all()
    total_bookings = len(bookings)
    available_seats = theatre.capacity - sum(booking.num_seats for booking in bookings)



    for showing in theatre.showings:
        average_rating = showing.show.rating


    export_data = {
        'Theatre Name': theatre_details['theatrename'],
        'Location': theatre_details['location'],
        'Number of Shows': num_shows,
        'Total Bookings': total_bookings,
        'Available Seats': available_seats,
        'Average Show Rating': average_rating

    }

    return export_data


class export_csv(Resource):
    method_decorators = [token_required]

    def get(self, current_user):
        csv_data = io.StringIO()
        csv_writer = csv.writer(csv_data)
        csv_writer.writerow(['Theatre Name', 'Location', 'Number of Shows', 'Total Bookings', 'Available Seats', 'Average Show Rating'])

        theatre_id = request.args.get('theatreId')
  
 

        theatre = Theatre.query.filter_by(id=theatre_id).first()

        if theatre:
            theatre_details = export_theatre_details(theatre)

            # Write theatre details to CSV
            csv_writer.writerow([
                theatre_details['Theatre Name'],
                theatre_details['Location'],
                theatre_details['Number of Shows'],
                theatre_details['Total Bookings'],
                theatre_details['Available Seats'],
                theatre_details['Average Show Rating']
            ])

            csv_data.seek(0)
            filename = f'theatre_{theatre.theatrename}_details.csv'
            return Response(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename={}'.format(filename)})
        else:
            return {'message': 'Theatre not found'}, 404

api.add_resource(export_csv, '/export_csv')







# Get current user profile
class get_user(Resource):
    method_decorators = [token_required]

    # Get user data
    def get(self, current_user):
        user = user_data.query.filter_by(
            username=current_user.username).first()
        if user is None:
            return make_response(jsonify({'message': 'User not found!'}), 404)
        return make_response(jsonify({'user': user.serialize()}), 200)

api.add_resource(get_user, '/api/profile')

# Search for shows by tag
class SearchShowByTag(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.json
        tag = data.get('tag', '')

 
        shows = Show.query.filter(Show.tag.ilike(f'%{tag}%')).all()

        if not shows:
            return make_response(jsonify({'message': 'No shows found with the given tag'}), 404)

        shows = [show.serialize() for show in shows]
        return make_response(jsonify({'shows': shows}), 200)

api.add_resource(SearchShowByTag, '/api/search_shows_by_tag')

# Search for theatres by location
class SearchTheatreByLocation(Resource):
    method_decorators = [token_required]

    def post(self, current_user):
        data = request.json
        location = data.get('location', '')

        theatres = Theatre.query.filter(Theatre.location.ilike(f'%{location}%')).all()

        if not theatres:
            return make_response(jsonify({'message': 'No theatres found with the given location'}), 404)

        theatres = [theatre.serialize() for theatre in theatres]
        return make_response(jsonify({'theatres': theatres}), 200)

api.add_resource(SearchTheatreByLocation, '/api/search_theatres_by_location')




# Update user password
class update_password(Resource):
    method_decorators = [token_required]

    # Update user password
    def post(self, current_user):
        data = request.args
        user = user_data.query.filter_by(
            username=current_user.username).first()
        if user is None:
            return make_response(jsonify({'message': 'User not found!'}), 404)
        if not check_password_hash(user.password, data['old_password']):
            return make_response(jsonify({'message': 'Wrong password!'}), 400)
        user.password = generate_password_hash(
            data['new_password'], method='sha256')
        db.session.commit()
        return make_response(jsonify({'message': 'Password updated successfully!'}), 200)

api.add_resource(update_password, '/update_password')


# Create a function to create a default admin user
def create_default_admin(): 
    try:
        # Check if admin user already exists by username
        admin = user_data.query.filter_by(username='admin').first()
        if admin:
            db.session.delete(admin)
            db.session.commit()
            return

        # Hash the default admin password
        admin_password = 'admin'

        # Create the default admin user
        default_admin = user_data(
            name='Admin',
            surname='User',
            username='admin',
            password=admin_password,
            email='admin@example.com',
            public_id=str(uuid.uuid4()),
            is_admin=1
        )

        db.session.add(default_admin)
        db.session.commit()

    except Exception as e:
        print("Error creating default admin:", e)  # For debugging purposes


# Call the function to create the default admin user
create_default_admin()
db.create_all()
if __name__ == "__main__":
    create_default_admin()
    app.run(debug=True, host='0.0.0.0', port=5000)
