from flask_migrate import Migrate

from models import PG
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pg_life.db'

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']  # guest or owner
        new_user = User(name=name, email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
@app.route('/add_pg', methods=['GET', 'POST'])
@login_required
def add_pg():
    if current_user.role != 'owner':
        flash("Only PG owners can access this page.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        rent = request.form['rent']
        gender = request.form['gender']
        amenities = request.form['amenities']

        pg = PG(
            name=name,
            address=address,
            rent=rent,
            gender=gender,
            amenities=amenities,
            owner_id=current_user.id
        )
        db.session.add(pg)
        db.session.commit()
        flash("PG listing added successfully!")
        return redirect(url_for('owner_pgs'))

    return render_template('add_pg.html')
@app.route('/owner_pgs')
@login_required
def owner_pgs():
    if current_user.role != 'owner':
        flash("Only PG owners can access this page.")
        return redirect(url_for('dashboard'))

    listings = PG.query.filter_by(owner_id=current_user.id).all()
    return render_template('owner_pgs.html', pgs=listings)
@app.route('/pgs')
def view_pgs():
    gender = request.args.get('gender')
    search = request.args.get('search')

    # Base query
    query = PG.query

    if gender:
        query = query.filter(PG.gender == gender)
    if search:
        query = query.filter(
            PG.name.ilike(f'%{search}%') | PG.address.ilike(f'%{search}%')
        )

    all_pgs = query.all()
    return render_template('pgs.html', pgs=all_pgs)

@app.route('/pg/<int:pg_id>', methods=['GET', 'POST'])
def pg_detail(pg_id):
    pg = PG.query.get_or_404(pg_id)

    if request.method == 'POST':
        if not current_user.is_authenticated or current_user.role != 'student':
            flash("Login as a student to request booking.")
            return redirect(url_for('login'))

        message = request.form['message']
        request_obj = BookingRequest(pg_id=pg.id, user_id=current_user.id, message=message)
        db.session.add(request_obj)
        db.session.commit()
        flash("Booking request sent to the owner!")
        return redirect(url_for('pg_detail', pg_id=pg_id))

    return render_template('pg_detail.html', pg=pg)
@app.route('/owner/requests')
@login_required
def owner_requests():
    if current_user.role != 'owner':
        flash("Only PG owners can access this page.")
        return redirect(url_for('dashboard'))

    # Get all requests for PGs owned by this owner
    pgs = PG.query.filter_by(owner_id=current_user.id).all()
    pg_ids = [pg.id for pg in pgs]
    requests = BookingRequest.query.filter(BookingRequest.pg_id.in_(pg_ids)).all()

    return render_template('owner_requests.html', requests=requests)
@app.route('/owner/requests/<int:request_id>/<action>')
@login_required
def handle_request(request_id, action):
    if current_user.role != 'owner':
        flash("Only PG owners can perform this action.")
        return redirect(url_for('dashboard'))

    booking = BookingRequest.query.get_or_404(request_id)
    pg = PG.query.get(booking.pg_id)

    if pg.owner_id != current_user.id:
        flash("You are not authorized to update this request.")
        return redirect(url_for('dashboard'))

    if action in ['accept', 'reject']:
        booking.status = 'accepted' if action == 'accept' else 'rejected'
        db.session.commit()
        flash(f"Request has been {booking.status}.")

    return redirect(url_for('owner_requests'))


