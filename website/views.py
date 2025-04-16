from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import List
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def main():
    return render_template("main.html", user=current_user)

@views.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        list = request.form.get('list')
        list_title = request.form.get('list_title')

        if len(list) < 1 or len(list_title) < 1:
            flash('Too short!', category='error')
        else: 
            new_list = List(data=list, user_id=current_user.id, list_title=list_title)
            db.session.add(new_list)
            db.session.commit()
            flash('List added!', category='success')

    return render_template("home.html", user=current_user)

@views.route('/delete-list', methods=['POST'])
def delete_list():
    list = json.loads(request.data)
    listId = list['listId']
    list = List.query.get(listId)
    if list:
        if list.user_id == current_user.id:
            db.session.delete(list)
            db.session.commit()
    
    return jsonify({})

