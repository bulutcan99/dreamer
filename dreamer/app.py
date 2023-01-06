from flask import Flask, g, render_template, request, redirect, url_for, flash, session
from dotenv import load_dotenv
from user import UserModel, DreamModel
from flask_bcrypt import Bcrypt
import os

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")


def dream_list_by_name():
    dreams = DreamModel.find_all()
    dreams_with_names = []
    for dream in dreams:
        user = UserModel.find_by_id(dream.get_user_id())
        dreams_with_names.append((user.get_name_surname(), dream))

    return dreams_with_names

def dream_for_profile():
    if 'email' in session:
        email = session['email']
        me = UserModel.find_by_email(email=email)
        dreams = DreamModel.find_all_by_user_id(me.id)
        return dreams


@app.before_first_request
def create_tables():
    db.create_all()

def before_request():
    g.user = None
    if 'email' in session:
        users = UserModel.find_all()
        for i in users:
            if i.email == session['email']:
                g.user = user


@app.errorhandler(404)
def error(error):
    return render_template('hatakodu.html'), 404


@app.route('/', methods=["GET"])
def home():
    if 'email' in session:
        email = session['email']
        me = UserModel.find_by_email(email=email)
        name = me.get_name_surname()
        return render_template('home.html', me=me, dreams=dream_list_by_name(), name=name)
    return render_template('home.html', me=False, dreams=[])


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password)
        new_user = UserModel(name, surname, email, hashed_password)
        if UserModel.find_by_email(new_user.email):
            flash('Bu email ile bir hesap zaten daha öncesinde oluşturulmuştur!')
            return render_template('register.html')

        new_user.save_to_db()
        return render_template('home.html', me=True, dreams=dream_list_by_name())
    return render_template('register.html')


@app.route('/login', methods=["GET", "POST"])
def login():
    if 'email' in session:
        return render_template('home.html', me=True, dreams=dream_list_by_name())
    if request.method == "POST":
        session.pop('email', None)
        email = request.form.get("email")
        password = request.form.get("password")
        user = UserModel.find_by_email(email=email)
        if user and bcrypt.check_password_hash(user.password, password):
            session['email'] = email
            return render_template('home.html', me=True, dreams=dream_list_by_name())

        flash("Hatalı bir giriş yapıldı.")
    return render_template('login.html')



@app.route('/profile', methods=["GET"])
def profile():
    if 'email' in session:
        email = session['email']
        me = UserModel.find_by_email(email=email)
        dr = DreamModel.find_all_by_user_id(me.id)
        return render_template('profile.html', me=me, dreams=dr)
    return render_template('login.html', me=False, dreams=[])

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/create', methods=["GET", "POST"])
def create():
    if 'email' in session:
        email = session['email']
        me = UserModel.find_by_email(email=email)
        if request.method == 'POST':
            dream = request.form.get('dream')
            detail = request.form.get('detail')
            quote = request.form.get('quote')
            new_dream = DreamModel(dream=dream, detail=detail, quote=quote, user_id=me.id)
            new_dream.save_to_db()
            return render_template('home.html', me=True, dreams=dream_list_by_name())
    return render_template('create.html')


@app.route('/details')
def details():
    return render_template('details.html')


if __name__ == '__main__':
    from user import db

    db.init_app(app)

    app.run(debug=True)
