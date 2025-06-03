from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response, current_app
from flask_login import login_required, current_user
from .models import List, Task, Plant
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
            flash('Nazwa listy musi mieć przynajmniej 1 znak!', category='error')
        else: 
            new_list = List(user_id=current_user.id, list_title=list_title)
            db.session.add(new_list)
            db.session.commit()
            flash('Lista została dodana!', category='success')
            return redirect(url_for('views.go_to_list', list_id = new_list.id))
        
    user_lists = List.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', user=current_user, lists=user_lists)

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
        flash('Nie znaleziono listy.', category='error')
        return redirect(url_for('views.home'))
    
    if request.method == 'POST':
        task_data = request.form.get('task', '').strip()
        reminder = request.form.get('reminder')

        if not task_data:
            flash('Nazwa zadania musi mieć przynajmniej 1 znak!', category='error')
        else:
            if reminder:
                if request.form.get('deadline_date') and request.form.get('deadline_time'):
                    deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                    deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                    new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id, deadline_date = deadline_date, deadline_time = deadline_time, reminder = True)
                else:
                    flash('Wybierz datę i godzinę, aby móc otrzymać przypomnienie!', category='error')
                    return redirect(url_for('views.show_list', list_id=list_id), code=303)   
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
                    return redirect(url_for('views.show_list', list_id=list_id), code=303)
                else:
                    new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id)

            db.session.add(new_task)
            db.session.commit()
            flash('Dodano zadanie!', category='success')
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
    user = current_user

    task.if_done = 'if_done' in request.form

    if task.if_done:
        task.completed_at = datetime.now()
        if not task.first_check:
            task.first_check = True
            user.water_points += 1
            user.daily_checked_tasks += 1
    else:
        task.completed_at = None

    db.session.commit()
    return redirect(url_for('views.show_list', list_id=task.list_id))


@views.route('/update_task_calendar/<int:task_id>', methods=['POST'])
@login_required
def update_task_calendar(task_id):
    task = Task.query.get_or_404(task_id)
    user = current_user

    task.if_done = 'if_done' in request.form

    if task.if_done:
        task.completed_at = datetime.now()
        if not task.first_check:
            task.first_check = True
            user.water_points += 1
            user.daily_checked_tasks += 1
    else:
        task.completed_at = None

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
    # od dziś do roku w przód
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
        label = format_date_pretty(day_obj)
        if day_obj < today:
            past_days.append((iso, label))
        else:
            future_days.append((iso, label))

    if request.method == 'POST':
        action = request.form.get("action")

        if action == 'add_task':
            task_data = request.form.get('task', '').strip()
            list_id = request.form.get('list')
            reminder = request.form.get('reminder')

            if not task_data:
                flash('Zadanie musi mieć przynajmniej 1 znak!', category='error')
            else:
                if reminder:
                    if request.form.get('deadline_date') and request.form.get('deadline_time'):
                        deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                        deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                        new_task = Task(data=task_data, list_id=list_id, user_id=current_user.id, deadline_date = deadline_date, deadline_time = deadline_time, reminder = True)
                    else:
                        flash('Wybierz datę i godzinę, aby móc otrzymać przypomnienie!', category='error')
                        return redirect(url_for('views.calendar'), code=303)   
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
            flash('Dodano zadanie!', category='success')

            return redirect(url_for('views.calendar'), code=303)
        elif action == 'edit_task':
            task_id = request.form.get('task_id')
            task_data = request.form.get('task', '').strip()
            reminder = request.form.get('reminder')

            task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()

            if not task:
                flash('Nie znaleziono zadania.', category='error')
                return redirect(url_for('views.calendar'), code=303)

            if task_data:
                task.data = task_data
            else: 
                task.data = task.data

            if reminder:
                if request.form.get('deadline_date') and request.form.get('deadline_time'):
                    task.deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                    task.deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                    task.reminder = True
                    task.reminder_sent = False 
                else:
                    flash('Wybierz datę i godzinę, aby móc otrzymać przypomnienie!', category='error')
                    return redirect(url_for('views.calendar'), code=303)   
            else:
                if request.form.get('deadline_date') and request.form.get('deadline_time'):
                    task.deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                    task.deadline_time = datetime.strptime(request.form.get('deadline_time'), '%H:%M').time()
                elif request.form.get('deadline_time') and not request.form.get('deadline_date'):
                    flash('Wybierz datę, aby móc ustawić godzinę!', category='error')
                    return redirect(url_for('views.calendar'), code=303)
                elif request.form.get('deadline_date') and not request.form.get('deadline_time'):
                    task.deadline_date = datetime.strptime(request.form.get('deadline_date'), '%Y-%m-%d').date()
                else:
                    task.deadline_date = None
                    task.deadline_time = None
                task.reminder = False
                task.reminder_sent = False 

            db.session.commit()
            flash('Zadanie zaktualizowane!', category='success')
            return redirect(url_for('views.calendar'), code=303)

    
    return render_template(
        "calendar.html",
        events=events,
        tasks_by_date=tasks_by_date,
        future_days=future_days,
        past_days=past_days,
        user=current_user
    )

@views.route('/water_plant', methods=['POST'])
@login_required
def water_plant():
    user = current_user
    if user.water_points > 0:
        user.water_points -= 1

        goal = user.daily_task_goal or 1
        water_needed = int(goal * 0.5 + 0.999)

        if user.plant_wither_stage in [1, 2]:
            user.plant_rescue_progress += 1
            if user.plant_rescue_progress >= water_needed:
                user.plant_wither_stage = 0
                user.plant_rescue_progress = 0
                user.plant_withered_notification_sent = False
                user.plant_unwatered_days = 0
        elif user.plant_wither_stage == 0:
            user.plant_growth += 1

        db.session.commit()
    else: 
        flash('Zdobądź wodę, aby móc podlać roślinkę!', category='error')

    return redirect(request.form.get('next') or url_for('home'))

@views.route('/put_plant_on_shelf', methods=['POST'])
@login_required
def put_plant_on_shelf():
    user = current_user
    if user.plant_growth >= 3*user.daily_task_goal or user.plant_wither_stage == 3:
        if user.plant_wither_stage < user.plant_growth:
            final_growth = 1
        elif user.plant_wither_stage < 2*user.plant_growth:
            final_growth = 2
        elif user.plant_wither_stage < 3*user.plant_growth:
            final_growth = 3
        else:
            final_growth = 4
        new_plant = Plant(
            created_at = user.plant_created_at,
            finished_at = datetime.now(),
            user_id = user.id,
            final_growth = final_growth,       
            final_wither_stage = user.plant_wither_stage
        )
        db.session.add(new_plant)

        user.plant_created_at = datetime.now()
        user.plant_growth = 0
        user.plant_wither_stage = 0
        user.plant_unwatered_days = 0
        db.session.commit()
    flash('Roślinka została odłożona na półkę!', category='success')
    next_page = request.form.get('next') or url_for('home')
    return redirect(next_page)

@views.route('/plant-shelf', methods=['GET'])
@login_required
def plant_shelf():
    user = current_user
    plants = user.plants
    return render_template("plant_shelf.html", user=current_user, plants=plants)

@views.route('/update-daily-task-goal', methods=['POST'])
@login_required
def update_goal():
    user = current_user
    goal = request.form.get("daily-goal", type=int)
    if user.plant_growth == 0 and user.plant_wither_stage == 0:
        user.daily_task_goal = goal
        db.session.commit()
    elif user.plant_growth == 3*user.daily_task_goal or user.plant_wither_stage == 3:
        flash('Odstaw roślinkę na półkę, aby móc zmienić dzienny cel!', category='error')
    else:
        if goal >= user.daily_task_goal:
            user.daily_task_goal = goal
            db.session.commit()
        else:
            flash('Nie możesz zmienić dziennego celu na mniejszy, gdy roślinka jest w trakcie wzrostu!', category='error')
    next_page = request.form.get('next') or url_for('home')
    return redirect(next_page)