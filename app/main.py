from datetime import date

from flask import Flask, render_template, flash, redirect, url_for, request
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from database import db
from form import SignIn, SignUp, CreateTask
from model import User, ToDoList, Task

app = Flask(__name__)
app.config["SECRET_KEY"] = "top secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo_app_db.db"
bootstrap = Bootstrap5(app)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign-in"

bcrypt = Bcrypt(app)

with app.app_context():
    db.drop_all()
    db.create_all()



@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/sign-in", methods=["GET", "POST"])
def get_sign_in():
    form = SignIn()

    if form.validate_on_submit():

        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Login successful")

            return redirect(url_for("home"))
        else:
            flash("Invalid username or password")

    return render_template("sign-in.html", form=form)


@app.route("/sign-up", methods=["GET", "POST"])
def get_sign_up():
    form = SignUp()

    if form.validate_on_submit():

        if form.password.data != form.confirm_password.data:
            flash("Invalid username or password")

        else:
            user = User(
                None,
                form.email.data,
                form.username.data,
                bcrypt.generate_password_hash(form.password.data).decode('utf-8'),
            )

            user.to_do_list = ToDoList(user)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("get_sign_in"))

    return render_template("sign-up.html", form=form)


@login_required
@app.route("/all-tasks")
def get_all_tasks():
    completed = [task for task in current_user.to_do_list.tasks if task.is_completed]
    tasks = [task for task in current_user.to_do_list.tasks if task not in completed]

    return render_template("all-tasks.html", tasks=tasks, completed=completed)

@login_required
@app.route("/to-do-list")
def get_to_do_list():
    tasks = [task for task in current_user.to_do_list.tasks if task.is_completed is False]

    return render_template("to-do-list.html", tasks=tasks)

@login_required
@app.route("/completed-tasks")
def get_completed_tasks():
    completed = [task for task in current_user.to_do_list.tasks if task.is_completed]

    return render_template("completed-tasks.html", tasks=completed)


@login_required
@app.route("/create-task", methods=["GET", "POST"])
def get_create_task():
    form = CreateTask()

    if form.validate_on_submit():
        task = Task(form.title.data, form.task.data, current_user.to_do_list)

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("get_to_do_list"))

    return render_template("create-task.html", form=form)


@login_required
@app.route("/task/<int:task_id>")
def get_task(task_id):
    task = db.session.execute(db.select(Task).where(Task.id == task_id)).scalar()

    print(task)

    return render_template("task.html", task=task)

@app.route("/sign-out")
def do_sign_out():
    logout_user()

    return redirect(url_for("get_sign_in"))


@app.route("/mark-completed", methods=["GET", "POST"])
def mark_completed():
    completed_ids = [int(task_id) for task_id in request.form.values()]

    db.session.execute(
        db.update(Task)
        .where(Task.id.in_(completed_ids))
        .values(is_completed=True,
                completed_on=date.today()))

    db.session.commit()

    return redirect(url_for("get_completed_tasks"))


@app.route("/delete-tasks", methods=["GET", "POST"])
def delete_tasks():
    for_deletion_ids = [int(task_id) for task_id in request.form.values()]

    db.session.execute(
        db.delete(Task)
        .where(Task.id.in_(for_deletion_ids)))

    db.session.commit()

    return redirect(url_for("get_to_do_list"))


if __name__ == "__main__":
    app.run(debug=True)
