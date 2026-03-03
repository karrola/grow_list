# GrowList - ToDo Application

A simple task management application with gamification elements.

## Technologies

Python, Flask, SQLAlchemy, HTML5, CSS3

## Features

- Add, edit, and delete tasks
- Email reminders for deadlines
- Organize tasks into lists
- Calendar view
- Gamification – growing a plant 

## Live version

https://grow-list.onrender.com

## Local setup instructions

1. Clone the repository
2. (Recommended) Create a virtual environment
3. Install dependencies:
```
pip install -r requirements.txt
```
4. Create a `.env` file based on `.env.example`
5. Apply database migrations:
```
flask db upgrade
```
6. Run the development server:
```
flask run
```

The application will be available at: http://127.0.0.1:5000/

## Browser notes

The application works best in Firefox – this browser was used during development, so there should be no display or functionality issues.

## Test routes

The file `test.py` contains test routes to simulate application behavior:

- `/test_1_day`, `/test_2_days`, `/test_3_days`, `/test_4_days` – simulate plant wilting after x days and sending notifications about its status
- `/run_reminders` – send notifications about task deadlines (only tasks due within 24 hours)
- `/reset_daily_tasks` – reset the number of tasks completed in a day

> For testing purposes, in `scheduler.py`, inside the function `update_plant_health_status`, the code that checks the number of tasks completed the previous day is commented out. Instead, the value is set to 0, so the test routes for simulating plant wilting always work.

## Notes on email notifications

The application is set up to send email notifications. However, in the Render production environment, outbound SMTP is blocked. Therefore, calls to the `send_email` function are currently simulated (logged to the console) on Render.

Locally, after configuring the environment variables
`MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER`, etc., emails are sent properly.
