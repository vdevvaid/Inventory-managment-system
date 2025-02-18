from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Required for session management
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Item Model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('signup'))
            
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists!')
            return redirect(url_for('signup'))
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    items = Item.query.all()
    return render_template('dashboard.html', items=items)

# Add business-specific validation
def validate_item_quantity(quantity):
    try:
        qty = int(quantity)
        if qty < 0:
            raise ValueError("Quantity cannot be negative")
        if qty > 10000:
            raise ValueError("Quantity exceeds maximum limit")
        return qty
    except ValueError as e:
        raise ValueError("Invalid quantity value")

# Add business rules
@app.route('/add_item', methods=['POST'])
@login_required
def add_item():
    try:
        name = request.form.get('name').strip()
        quantity = request.form.get('quantity')
        description = request.form.get('description').strip()
        
        # Business validations
        if len(name) < 3:
            flash('Item name must be at least 3 characters long', 'error')
            return redirect(url_for('dashboard'))
            
        quantity = validate_item_quantity(quantity)
        
        # Check for duplicate items
        existing_item = Item.query.filter(Item.name.ilike(name)).first()
        if existing_item:
            flash('An item with this name already exists', 'error')
            return redirect(url_for('dashboard'))
            
        new_item = Item(name=name, quantity=quantity, description=description)
        db.session.add(new_item)
        db.session.commit()
        
        flash(f'Item "{name}" added successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    except ValueError as e:
        flash(str(e), 'error')
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('dashboard'))

@app.route('/edit_item/<int:item_id>', methods=['POST'])
@login_required
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    
    item.name = request.form.get('name')
    item.quantity = request.form.get('quantity')
    item.description = request.form.get('description')
    
    db.session.commit()
    flash('Item updated successfully!')
    return redirect(url_for('dashboard'))

@app.route('/delete_item/<int:item_id>')
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    
    flash('Item deleted successfully!')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True) 