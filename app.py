from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import datetime
import os.path
import psycopg2
app = Flask(__name__)

pg_user = "postgres"
pg_host = "localhost"
pg_pwd = "4221"
pg_port = "5432"
pg_db = "symbol_api"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{username}:{password}@{host}:{port}/{database}".format(username=pg_user, password=pg_pwd, host=pg_host, port=pg_port, database=pg_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False


check_exist = open("check.txt", "r")
exist = check_exist.read()
exist = bool(exist)
print(exist)
csv_file_path = "posts.csv"
db = SQLAlchemy(app)
def LoadData():
    csv_1 = pd.read_csv('save_me.csv')
    return csv_1


class posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created_date = db.Column(db.Date)
    rubrics = db.Column(db.Text)

    def __repr__(self):
        return '<Article %r>' % self.id




if (not(exist)):
    con = psycopg2.connect(
        host=pg_host,
        database=pg_db,
        user=pg_user,
        password=pg_pwd
    )
    cur = con.cursor()
    cur.execute("create table if not exists posts(id BIGSERIAL PRIMARY KEY NOT NULL, text text, created_date date, rubrics text)")
    cur.execute("SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_NAME= %s", ("unique_id",))
    unique_id_exists = cur.fetchone() 
    if(not(unique_id_exists)):
        cur.execute("ALTER TABLE posts add constraint unique_id UNIQUE (id)")
    con.commit()

    print("Entered")
    data = LoadData()
    file_name = "posts.csv"
    print(type(data))
    for i in range(len(data)):
        current = data.iloc[i]
        current_text = current.text
        current_created_date = current.created_date
        current_created_date = datetime.datetime.strptime(current_created_date, '%Y-%m-%d %H:%M:%S')
        current_rubrics = current.rubrics
        record = posts(text=current_text, created_date=current_created_date, rubrics=current_rubrics)
        db.session.add(record)
    db.session.commit()
    file1 = open("check.txt", "a")
    file1.write('1')
    file1.close()
    con.close()
    cur.close()

@app.route("/", methods=['EXIT', 'GET'])
@app.route("/home", methods=['EXIT', 'GET'])
def index():
    if request.method=="EXIT":
        return 0
    else:
        return render_template("index.html")


@app.route("/posts", methods=['POST', 'GET'])
def posts_show():
    if request.method == "POST":
        target_message = request.form['text']
        target_message=target_message.strip()
        articles = posts.query.filter(posts.text.contains(target_message)).order_by(posts.created_date.desc()).limit(20)
        return render_template("posts.html", articles=articles, target_message=target_message)
    else:
        articles = posts.query.order_by(posts.created_date.desc()).limit(20)
        return render_template("posts.html", articles=articles)


@app.route("/posts/<int:id>")
def posts_det(id):
    article = posts.query.get(id)
    return render_template("post_det.html", article=article)


@app.route("/posts/<int:id>/delete")
def posts_delete(id):
    article = posts.query.get_or_404(id)
    try:
        db.session.delete(article)
        db.session.commit()
        return redirect('/posts')
    except:
        return "Ошибка при удалении статьи"

@app.route("/posts/<int:id>/update", methods =['POST', 'GET'])
def note_update(id):
    article = posts.query.get(id)
    if request.method == "POST":
        article.text = request.form['text']
        try:
            db.session.commit()
            return redirect('/posts')
        except:
            return "Error"

    else:
        return render_template("post_update.html", article=article)

@app.route("/about")
def about():
    return render_template("about.html")




if __name__ == "__main__":
    app.run(port="5000", debug=True)
