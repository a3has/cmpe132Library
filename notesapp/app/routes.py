from flask import render_template, flash, redirect, url_for, request
from app import app, db
from forms import LoginForm, NoteForm
from flask_login import current_user, login_user, logout_user, login_required
from models import Note, User, Todo
from werkzeug.urls import url_parse
from forms import RegistrationForm, AdvancedSearchForm


@app.route('/')
@app.route('/index')
@login_required
def index():
    # user = {'username': 'Aboudi'}
    posts = [
        {
            # 'author': {'username': 'John'},
            'body': 'This is the post login landing page.'
        },
        {
            # 'author': {'username': 'Susan'},
            'body': 'Work in progress. Need to give names for each note instead of "username" says.'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':

        user_data = {
            'name': request.form.get('name'),
            'biography': request.form.get('biography')
        }

        print("Updated user data:", user_data)

    return render_template('userprofile.html')

@app.route('/todo')
def todo():
    todo_list = Todo.query.filter_by(user_id=current_user.id).all()
    #todo_list = current_user.Todo.all()
    #todo_list=Todo.query.all()
    return render_template('todo.html',todo_list=todo_list)

@app.route('/add',methods=['POST'])
def add():
    name = request.form.get("name")
    new_task=Todo(name=name,done=False,user_id=current_user.id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route('/update/<int:todo_id>')
def update(todo_id):
    todo= Todo.query.get(todo_id)
    todo.done=not todo.done
    db.session.commit()
    return redirect(url_for("todo"))


@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo= Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route('/advanced_searching', methods=['GET', 'POST'])
def advanced_search():
    form = AdvancedSearchForm()

    if form.validate_on_submit():
        # Build the query based on form input
        query = Todo.query

        if form.task_name.data:
            query = query.filter(Todo.name.ilike(f'%{form.task_name.data}%'))

        if form.is_complete.data is not None:
            query = query.filter(Todo.done == form.is_complete.data)

        # Execute the query for all 
        results = query.all()

        return render_template('search_results.html', results=results)

    return render_template('adv_search.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/notes')
def show_notes():
    notes = Note.query.all()
    return render_template('notes.html', notes=notes)

@app.route('/create_note', methods=['GET', 'POST'])
def create_note():
    form = NoteForm()

    if form.validate_on_submit():
        content = form.content.data
        new_note = Note(content=content)
        db.session.add(new_note)
        db.session.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('show_notes'))

    return render_template('create_note.html', form=form)

