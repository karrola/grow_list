from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, List
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
               flash('Zalogowano!', category='success')
               login_user(user, remember=True)
               return redirect(url_for('views.home')) 
            else:
                flash('Niepoprawne hasło, spróbuj ponownie.', category='error')
        else:
            flash('Nie istnieje konto o takim adresie e-mail.', category='error')
    
    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Wylogowano!', category='success')
    return redirect (url_for('views.main'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Konto o takim adresie e-mail już istnieje.', category='error')
        elif len(email) < 4:
            flash('E-mail musi być dłuższy niż 3 znaki.', category='error')
        elif len(first_name) < 2:
            flash('Nazwa użytkownika musi być dłuższa niż 1 znak.', category='error')
        elif password1 != password2:
            flash('Hasła do siebie nie pasują.', category='error')
        elif len(password1) < 7:
            flash('Hasło musi mieć minimum 7 znaków.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.flush()

            default_list = List(list_title="Skrzynka", user_id=new_user.id, is_default=True)
            db.session.add(default_list)

            db.session.commit()

            login_user(new_user, remember=True)
            flash('Konto zostało utworzone!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)