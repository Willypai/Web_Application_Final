from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    reminders = db.relationship('Reminder', backref='owner', lazy=True)

# Reminder model
class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(250), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('reminders'))  # Redirect to reminders page
        flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/profile')
@login_required
def profile():
    return f'Hello, {current_user.username}! Welcome to your profile.'

@app.route('/reminders', methods=['GET', 'POST'])
@login_required
def reminders():
    if request.method == 'POST':
        content = request.form['content']
        new_reminder = Reminder(content=content, owner=current_user)
        db.session.add(new_reminder)
        db.session.commit()
        flash('Reminder added!', 'success')
        return redirect(url_for('reminders'))

    user_reminders = Reminder.query.filter_by(user_id=current_user.id).all()
    return render_template('reminders.html', reminders=user_reminders)

@app.route('/edit_reminder/<int:reminder_id>', methods=['GET', 'POST'])
@login_required
def edit_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    if request.method == 'POST':
        reminder.content = request.form['content']
        db.session.commit()
        flash('Reminder updated!', 'success')
        return redirect(url_for('reminders'))
    return render_template('edit_reminder.html', reminder=reminder)

@app.route('/delete_reminder/<int:reminder_id>')
@login_required
def delete_reminder(reminder_id):
    reminder = Reminder.query.get_or_404(reminder_id)
    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted!', 'success')
    return redirect(url_for('reminders'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
