from flask import Flask, url_for, request, render_template
from app import app
import redis
import random

r = redis.StrictRedis(host='localhost', port = 6379, db=0, charset="utf-8", decode_responses=True)

def get_task_list_html():
    return "".join(["<div>" + task + r"</div>" for task in get_task_list()])

@app.route('/')
def hello():
    create_link = "<a href=" + url_for('create') + '>Create a question</a>'
    return """<html>
                <head>
                    <title>Hello World!</title>
                </head>
                <body>
                """+ create_link + """
                </body>
                </html>"""

@app.route('/tasklist')
def task_list():
    all_tasks = r.keys()
    task_dict = {}
    for task in all_tasks:
        tmp = task.split(":")
        if tmp[0] not in task_dict:
            task_dict[tmp[0]] = [tmp[1]]
        else:
            task_dict[tmp[0]].append(tmp[1])
    task_list = []
    for key in task_dict:
        if key == "routines":
            task_list.append(task_dict[key])
        else:
            task_list.append(random.choice(task_dict[key]))
    return render_template('TaskList.html', task_list = task_list)

@app.route('/addtask', methods=['GET', 'POST'])
def add_task():
    if request.method == 'GET':
        return render_template('AddTask.html')
    elif request.method == 'POST':
        category = request.form['category']
        task = request.form['task']
        #Store data in DB
        r.set(category + ":" + task, 1)
        return render_template('CreatedQuestion.html', question = task)


@app.route('/alltasks', methods=['GET', 'POST'])
def all_tasks():
    if request.method == 'GET':
        all_tasks = r.keys()
        return render_template('AllTasks.html', task_list = all_tasks)
    elif request.method == 'POST':
        selected_tasks = request.form.getlist("tasks")
        for task in selected_tasks:
            r.delete(task)
        return render_template('AllTasks.html', task_list = selected_tasks)





# server/create
@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        all_tasks = r.keys()
        return render_template('AllTasks.html', task_list = all_tasks)
    elif request.method == 'POST':
        #read form data and save it
        title = request.form['title']
        answer  = request.form['answer']
        question = request.form['question']
        #Store data in DB
        r.set(title + ':question', question)
        r.set(title + ':answer', answer)
        return render_template('CreatedQuestion.html', question = question)

    else:
        return "<h2>Invalid request</h2>"
    return "<h2>This is the create page!</h2>"

# server/question/<title>
@app.route('/question/<title>', methods=['GET', 'POST'])
def question(title):
    if request.method == 'GET':
        #read question from DB
        question = r.get(title + ':question')
        return render_template('AnswerQuestion.html', question = question)
    elif request.method == 'POST':
        submittedAnswer = request.form['submittedAnswer']
        #Read answer from data store
        answer = r.get(title + ':answer')
        if submittedAnswer == answer:
            return render_template('Correct.html')
        else:
            return render_template('Incorrect.html', submittedAnswer = submittedAnswer, answer = answer)
    else:
        return "<h2>Invalid request</h2>"
    return "<h2>" + title + "</h2>"
