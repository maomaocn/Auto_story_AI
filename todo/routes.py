# 待办事项相关的路由和视图函数
from flask import Blueprint, render_template, request, redirect, url_for
from models import TodoItem
todo_bp = Blueprint('todo', __name__,template_folder='templates')
# --- 视图函数 ---
@todo_bp.route('/')
def index():
    """显示所有待办事项"""
    tasks = TodoItem.get_all()
    return render_template('index.html', tasks=tasks)