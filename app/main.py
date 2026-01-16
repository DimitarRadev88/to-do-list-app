from flask import Flask, render_template, flash, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from database import db
from form import SignIn, SignUp, CreateTask
from models import User, ToDoList, Task

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
    db.create_all()
    # user = User(
    #     None,
    #     "asd@asd.asd",
    #     "asd@asd.asd",
    #     bcrypt.generate_password_hash("asd").decode('utf-8'),
    # )
    #
    # user.to_do_list = ToDoList(user)
    #
    # db.session.add(user)
    # db.session.commit()


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

            return redirect(url_for("get_to_do_list"))
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
@app.route("/to-do-list")
def get_to_do_list():
    print(current_user.to_do_list.tasks)

    return render_template("to-do-list.html", tasks=list(current_user.to_do_list.tasks))


@login_required
@app.route("/create-task", methods=["GET", "POST"])
def get_create_task():
    form = CreateTask()

    if form.validate_on_submit():
        task = Task(form.task.data, current_user.to_do_list)

        db.session.add(task)
        db.session.commit()

        return redirect(url_for("get_to_do_list"))

    return render_template("create-task.html", form=form)


@app.route("/sign-out")
def get_sign_out():
    logout_user()

    return redirect(url_for("get_sign_in"))


if __name__ == "__main__":
    app.run(debug=True)
