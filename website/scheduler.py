from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, date, time
from website.models import User, db, Task
from flask_mail import Message
from . import mail
from flask import current_app
import math

def send_email(to, subject, body):
    msg = Message(subject, sender="growlist.app@gmail.com", recipients=[to])
    msg.body = body
    mail.send(msg)


def check_tasks_and_send_emails():
    with current_app.app_context():
        now = datetime.now()
        deadline_limit = now + timedelta(hours=24)

        tasks = Task.query.all()
        for task in tasks:
            if task.deadline_date and task.deadline_time:
                deadline_dt = datetime.combine(
                    task.deadline_date,
                    task.deadline_time
                )

                if now <= deadline_dt <= deadline_limit and task.reminder and not task.reminder_sent:
                    send_email(
                        task.user.email,
                        "Przypomnienie - dziś mija termin twojego zadania!",
                        f"Przypominamy, twoje zadanie {task.data} ma ustawiony deadline na {deadline_dt.strftime('%Y-%m-%d %H:%M')}."
                    )
                    task.reminder_sent = True

        db.session.commit()

def update_plant_health_status():
    today = date.today()
    yesterday = today - timedelta(days=1)

    users = User.query.all()
    for user in users:
        if user.plant_growth is None or user.plant_growth == 3 * user.daily_task_goal:
            continue

        # Zadania wykonane wczoraj
        tasks_completed_yesterday = Task.query.filter(
            Task.user_id == user.id,
            Task.completed_at >= datetime.combine(yesterday, time.min),
            Task.completed_at <=  datetime.combine(yesterday, time.max)
        ).count()

        water_needed = math.ceil(user.daily_task_goal / 2)

        if tasks_completed_yesterday < water_needed:
            user.plant_unwatered_days += 1
            user.plant_rescue_progress = 0

            if user.plant_unwatered_days == 2:
                user.plant_wither_stage = 1
            elif user.plant_unwatered_days == 3:
                user.plant_wither_stage = 2
            elif user.plant_unwatered_days >= 4:
                user.plant_wither_stage = 3
    
    
        if user.plant_wither_stage > 0 and user.plant_wither_stage != 3:
            send_email(
                            user.email,
                            "Twoja roslinka usycha :c",
                            f"Uwaga, twoja roślinka usycha! Wejdź do aplikacji i podlej ją, aby ją uratować."
                        )
        
        if user.plant_wither_stage == 3 and not user.plant_withered_notification_sent:
            send_email(
                            user.email,
                            "Twoja roślinka uschnęła :c",
                            f"Niestety, twoja roślinka nie została podlana przez 4 dni, przez co uschnęła. Ale nie poddawaj się - możesz zacząć hodować kolejną!"
                        )
            user.plant_withered_notification_sent = True

    db.session.commit()

def reset_daily_checked_tasks():
    users = User.query.all()
    for user in users:
        user.daily_checked_tasks = 0
    db.session.commit()

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    # Zadanie: wysyłka maili – codziennie o 7:00
    scheduler.add_job(
        func=lambda: with_app_context(app, check_tasks_and_send_emails),
        trigger='cron',
        hour=7,
        minute=0
    )

    # Zadanie: aktualizacja zdrowia roślin – codziennie o 00:00
    scheduler.add_job(
        func=lambda: with_app_context(app, update_plant_health_status),
        trigger='cron',
        hour=0,
        minute=0
    )

    # Zadanie: reset wykonanych w ciągu dnia zadań – codziennie o 00:00
    scheduler.add_job(
        func=lambda: with_app_context(app, reset_daily_checked_tasks),
        trigger='cron',
        hour=0,
        minute=0
    )

    scheduler.start()
        
def with_app_context(app, func):
    with app.app_context():
        func()