from flask import Blueprint, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from website import db
from website.scheduler import update_plant_health_status, check_tasks_and_send_emails, reset_daily_checked_tasks
from flask import app, Response
from flask_mail import Message
from website import mail 

test = Blueprint("test", __name__)

@test.route("/test_1_day")
@login_required
def test_1_day():
    current_user.plant_unwatered_days = 0
    db.session.commit()
    update_plant_health_status()
    flash("Aktualizacja roślin uruchomiona.", category="success")
    return redirect(url_for("views.home"))

@test.route("/test_2_days")
@login_required
def test_2_days():
    current_user.plant_unwatered_days = 1
    db.session.commit()
    update_plant_health_status()
    flash("Aktualizacja roślin uruchomiona.", category="success")
    return redirect(url_for("views.home"))

@test.route("/test_3_days")
@login_required
def test_3_days():
    current_user.plant_unwatered_days = 2
    db.session.commit()
    update_plant_health_status()
    flash("Aktualizacja roślin uruchomiona.", category="success")
    return redirect(url_for("views.home"))

@test.route("/test_4_days")
@login_required
def test_4_days():
    current_user.plant_unwatered_days = 3
    db.session.commit()
    update_plant_health_status()
    flash("Aktualizacja roślin uruchomiona.", category="success")
    return redirect(url_for("views.home"))

@test.route("/run_reminders")
@login_required
def run_reminders():
    check_tasks_and_send_emails()
    flash("Przypomnienia wysłane.", category="success")
    return redirect(url_for("views.home"))

@test.route("/send-test-email")
@login_required
def send_test_email():
    recipient = "example@wp.pl"

    try:
        msg = Message(
            subject="Growlist",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[recipient],
            body="To jest mail wysłany z aplikacji Growlist"
        )
        mail.send(msg)
        return Response(f"E-mail wysłany do: {recipient}", status=200)
    except Exception as e:
        print(f"Błąd podczas wysyłania: {e}")
        return Response(f"Błąd podczas wysyłania: {str(e)}", status=500)
    
@test.route("/reset_daily_tasks")
@login_required
def reset_daily_tasks():
    reset_daily_checked_tasks()
    flash("Wykonane zadania zresetowane.", category="success")
    return redirect(url_for("views.home"))