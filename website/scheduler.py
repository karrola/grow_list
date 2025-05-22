from apscheduler.schedulers.background import BackgroundScheduler
from website.views import check_tasks_and_send_emails

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    
    # Codziennie o 7:00
    scheduler.add_job(
        func=lambda: check_tasks_and_send_emails(),
        trigger='cron',
        hour=7,
        minute=0
    )

    scheduler.start()

    # Uruchom natychmiast po starcie aplikacji (na potrzeby testów)
    with app.app_context():
        check_tasks_and_send_emails()