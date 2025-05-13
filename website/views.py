from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response
from flask_login import login_required, current_user
from .models import List, Task
from . import db
import json
from datetime import datetime, timedelta, date
from collections import defaultdict
import calendar as calendar_lib
import locale


views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def main():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    else:
        return render_template('main.html', user=current_user)

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        list_title = request.form.get('list_title', '').strip()

        if not list_title:
            flash('Too short!', category='error')
        else: 
            new_list = List(user_id=current_user.id, list_title=list_title)
            db.session.add(new_list)
            db.session.commit()
            flash('List added!', category='success')
            return redirect(url_for('views.go_to_list', list_id = new_list.id))
        
    user_lists = List.query.filter_by(user_id=current_user.id).all()
    response = make_response(render_template('home.html', user=current_user, lists=user_lists))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@views.route('/redirect-to-list')
@login_required
def go_to_list():
    list_id = request.args.get('list_id')
    if not list_id:
        return redirect(url_for('views.home'))
    return redirect(url_for('views.show_list', list_id=list_id))
    

@views.route('/<int:list_id>', methods=['GET', 'POST'])
@login_required
def show_list(list_id):
    current_list = List.query.filter_by(id=list_id, user_id=current_user.id).first()

    if not current_list:
        flash("List not found.", category="error")
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        task_data = request.form.get('task', '').strip()

        if not task_data:
            flash('Too short!', category='error')
        else:
            if request.form.get('deadline_date') and request.form.get('deadline_time'):
                deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                new_task = Task(data=task_data, list_id=current_list.id, user_id=current_user.id, deadline_date = deadline_date, deadline_time = deadline_time)
            elif request.form.get('deadline_date') and not request.form.get('deadline_time'):
                deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                new_task = Task(data=task_data, list_id=current_list.id, user_id=current_user.id, deadline_date = deadline_date)
            elif request.form.get('deadline_time') and not request.form.get('deadline_date'):
                flash('Wybierz datę, aby móc ustawić godzinę!', category='error')
                return redirect(url_for('views.show_list', list_id=list_id), code=303)
            else:
                new_task = Task(data=task_data, list_id=current_list.id, user_id=current_user.id)

            db.session.add(new_task)
            db.session.commit()
            flash('Task added!', category='success')
            return redirect(url_for('views.show_list', list_id=list_id), code=303)

    return render_template('list.html', list=current_list, user=current_user)


@views.route('/delete-list', methods=['POST'])
@login_required
def delete_list():
    list = json.loads(request.data)
    listId = list['listId']
    list = List.query.get(listId)
    if list:
        if list.user_id == current_user.id:
            db.session.delete(list)
            db.session.commit()
    
    return jsonify({})

@views.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.if_done = 'if_done' in request.form
    db.session.commit()
    return redirect(url_for('views.show_list', list_id = task.list_id))

@views.route('/update_task_calendar/<int:task_id>', methods=['POST'])
@login_required
def update_task_calendar(task_id):
    task = Task.query.get_or_404(task_id)
    task.if_done = 'if_done' in request.form
    db.session.commit()

    return redirect(url_for('views.calendar'), code=303)

@views.route('/delete-task', methods=['POST'])
@login_required
def delete_task():
    task = json.loads(request.data)
    taskId = task['taskId']
    task = Task.query.get(taskId)
    if task:
        if task.user_id == current_user.id:
            db.session.delete(task)
            db.session.commit()
    
    return jsonify({})

@views.route("/calendar", methods=['POST', 'GET'])
@login_required
def calendar():
    # Ustalamy zakres dat: od dziś do roku w przód
    today = datetime.now().date()
    start_date = today - timedelta(days=365)
    end_date = today + timedelta(days=365)
    
    tasks = Task.query.filter(Task.deadline_date.isnot(None)).all()

    events = [
        {
            "title": task.data,
            "start": task.deadline_date.strftime("%Y-%m-%d"),
            "allDay": True
        }
        for task in tasks
        if today <= task.deadline_date <= end_date
    ]

    tasks_by_date = defaultdict(list)
    for task in tasks:
        if task.deadline_date:
            ds = task.deadline_date.strftime("%Y-%m-%d")
            if start_date <= task.deadline_date <= end_date:
                tasks_by_date[ds].append(task)

    tasks_by_date = dict(tasks_by_date)
    
    # Zakres od roku temu do roku wprzód
    today = datetime.now().date()
    start_date = today - timedelta(days=365)
    end_date = today + timedelta(days=365)

    all_days = [
        start_date + timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    dni = ['poniedziałek', 'wtorek', 'środa', 'czwartek', 'piątek', 'sobota', 'niedziela']
    miesiące = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca',
            'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']

    def format_date_pretty(date_obj):
        day = date_obj.day
        month = miesiące[date_obj.month - 1]
        weekday = dni[date_obj.weekday()]
        return f"{day} {month} - {weekday}"

    past_days = []
    future_days = []
    for day_obj in all_days:
        iso = day_obj.strftime("%Y-%m-%d")
        label = format_date_pretty(day_obj)      # np. "8 maj, czwartek"
        if day_obj < today:
            past_days.append((iso, label))
        else:
            future_days.append((iso, label))

    if request.method == 'POST':
        task_data = request.form.get('task', '').strip()
        list_id = request.form.get('list')

        if not task_data:
            flash('Too short!', category='error')
        else:
            if request.form.get('deadline_date') and request.form.get('deadline_time'):
                deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id, deadline_date = deadline_date, deadline_time = deadline_time)
            elif request.form.get('deadline_date') and not request.form.get('deadline_time'):
                deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id, deadline_date = deadline_date)
            elif request.form.get('deadline_time') and not request.form.get('deadline_date'):
                flash('Wybierz datę, aby móc ustawić godzinę!', category='error')
                return redirect(url_for('views.calendar'), code=303)
            else:
                new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id)

        db.session.add(new_task)
        db.session.commit()
        flash('Task added!', category='success')

        return redirect(url_for('views.calendar'), code=303)
    
    return render_template(
        "calendar.html",
        events=events,
        tasks_by_date=tasks_by_date,
        future_days=future_days,
        past_days=past_days,
        user=current_user
    )