from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response
from flask_login import login_required, current_user
from .models import List, Task
from . import db
import json
from datetime import datetime, timedelta, date
from collections import defaultdict
import calendar as calendar_lib


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
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.if_done = 'if_done' in request.form
    db.session.commit()
    return redirect(url_for('views.show_list', list_id = task.list_id))

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

@views.route("/calendar")
def calendar():
    # Ustalamy zakres dat: od dziś do roku w przód
    today = datetime.now().date()
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

    events_by_date = defaultdict(list)
    for event in events:
        date = event["start"]
        events_by_date[date].append(event)

    # Tworzymy dni w przyszłości (od dziś do roku wprzód)
    future_days = [
        (today + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(366)
    ]

    # Przeszłe dni od dziś wstecz do roku temu (w kolejności od najnowszego do najstarszego)
    all_past_days = [
        (today - timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(1, 366)
    ]

    return render_template(
        "calendar.html",
        events=events,
        events_by_date=events_by_date,
        future_days=future_days,
        all_past_days=all_past_days,
        user=current_user
    )