# coding=utf-8
from flask import Flask, url_for, render_template, redirect, request
from flask_wtf import FlaskForm
from data.category import Category
from data.news import News
from data.users import User
from data import db_session
from sqlalchemy.orm import object_session
from LoginForm import LoginForm
from RegisterForm import RegisterForm
from NewsForm import NewsForm
from flask_restful import reqparse, abort, Api, Resource
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
from news_resources import NewsListResource, NewsResource
from user_resources import UserListResource, UserResource


def main():
    global session
    db_session.global_init("db/blogs.sqlite")
    session = db_session.create_session()
    app.run(port=8080, host='127.0.0.1')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
api = Api(app)
api.add_resource(NewsListResource, '/api/news')
api.add_resource(NewsResource, '/api/news/<int:news_id>')
api.add_resource(UserListResource, '/api/users')
api.add_resource(UserResource, '/api/user/<int:user_id>')
login_manager = LoginManager()
login_manager.init_app(app)


parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('about', required=False)
parser.add_argument('email', required=True, type=str)
parser.add_argument('password', required=True, type=str)

@login_manager.user_loader
def load_user(user_id):
    global session
    return session.query(User).get(user_id)

@app.route('/news_add',  methods=['GET', 'POST'])
@login_required
def add_news():
    global session
    form = NewsForm()
    if form.validate_on_submit():
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
      #  a=len(session.query(Category).all())
      #  f = form.img_url.data
       # news.img_url=a+1
       # out = open("img{}.jpg".format('a+1'), "wb")
       # print(f)
       # out.write(f)
       # out.close        
        for i in form.categories.data.lower().split(', '):
            categ=session.query(Category).filter(Category.name == i).first()
            if not categ:
                category=Category()
                category.name=i
                news.categories.append(category)
            else:
                news.categories.append(categ)                
        print(session.hash_key, 'now')
        cur1session = object_session(current_user)
        print(cur1session.hash_key,'user')
        cursession = object_session(news)
        try:
            print(cursession.hask_key, 'news')
        except BaseException:
            print('no hash_key')        
        if cur1session.hash_key != session.hash_key:
            current_user.news.append(news)
            session.merge(current_user)
            session.commit() 
        else:
            current_user.news.append(news)
            session.merge(current_user)
            session.commit()
        return redirect('/')
    return render_template('add.html', title='Добавление новости', 
                           form=form)

@app.route('/')
@app.route("/news")
def news():
    global session
    if current_user.is_authenticated:
        news = session.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = session.query(News).filter(News.is_private != True)
    cats=[]
    leng=0
    for i in news:
        strin=[]
        leng+=1
        for j in i.categories:
            strin.append(j.name)
        cats.append(', '.join(strin))
    return render_template("news.html", news=news, cats= cats, leng=leng)

@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    global session
    news = session.query(News).filter(News.id == id,
                                      News.user == current_user).first()
    if news:
        session.delete(news)
        session.commit()
    else:
        abort(404)
    return redirect('/')        

@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    global session
    form = NewsForm()
    if request.method == "GET":
        news = session.query(News).filter(News.id == id, 
                                          News.user == current_user).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
            strin=[]
            for j in news.categories:
                strin.append(j.name)            
            form.categories.data = ', '.join(strin)
        else:
            abort(404)
    if form.validate_on_submit():
        news = session.query(News).filter(News.id == id, 
                                          News.user == current_user).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            
            news.categories=[]   
                
            for i in form.categories.data.lower().split(', '):
                categ=session.query(Category).filter(Category.name == i).first()
                if not categ:
                    category=Category()
                    category.name=i
                    news.categories.append(category)
                else:
                    news.categories.append(categ)
            current_user.news.append(news)
            session.merge(current_user)
            session.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('add.html', title='Редактирование новости', form=form)


@app.route('/index')
def index():
    return "Привет, Яндекс!"

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/login', methods=['GET', 'POST'])
def login():
    global session
    form = LoginForm()
    if form.validate_on_submit():
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)



@app.route('/register', methods=['GET', 'POST'])
def reqister():
    global session
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)



if __name__ == '__main__':
    main()