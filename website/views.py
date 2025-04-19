from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, make_response
from flask_login import login_required, current_user
from .models import List, Task
from . import db
import json

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
        list_title = request.form.get('list_title')

        if not list_title or len(list_title.strip()) < 1:
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
        task_data = request.form.get('task')

        if not task_data or len(task_data.strip()) < 1:
            flash('Too short!', category='error')
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

