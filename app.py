from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import datetime
import os.path
import psycopg2
app = Flask(__name__)

pg_user = "postgres"        ### These lines should be corrected in accordance with your server config
pg_host = "localhost"       ### 
pg_pwd = "4221"             ###
pg_port = "5432"            ###
pg_db = "symbol_api"        ###
csv_file_path = "posts.csv"
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://{username}:{password}@{host}:{port}/{database}".format(username=pg_user, password=pg_pwd, host=pg_host, port=pg_port, database=pg_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

    
check_exist = open("check.txt", "r")    ### The first step is reading file
exist = check_exist.read()              ### If file is empty server starting for the first time
exist = bool(exist)                     ### We will save information about it in boolean <exist>
if(exist):
    print("Starting without initialization")
else:
    print("Initialization started")

db = SQLAlchemy(app)                    ### declaring a db
def LoadData():
    csv_1 = pd.read_csv(csv_file_path)  ### reading csv file with pandas to save encoding
    return csv_1


class posts(db.Model):                  ### declaring a table
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    created_date = db.Column(db.Date)
    rubrics = db.Column(db.Text)

    def __repr__(self):
        return '<Post %r>' % self.id




if (not(exist)):                        ### If we are going to init our database
    con = psycopg2.connect(             ### we should connect to database 
        host=pg_host,                   ### create tables
        database=pg_db,                 ### and add constraint
        user=pg_user,
        password=pg_pwd
    )
    cur = con.cursor()
    cur.execute("create table if not exists posts(id BIGSERIAL PRIMARY KEY NOT NULL, text text, created_date date, rubrics text)")
    cur.execute("truncate posts cascade")
    cur.execute("SELECT * FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS WHERE CONSTRAINT_NAME= %s", ("unique_id",))
    unique_id_exists = cur.fetchone() 
    print("Initialization done")
    if(not(unique_id_exists)):
        cur.execute("ALTER TABLE posts add constraint unique_id UNIQUE (id)")
    con.commit()
    data = LoadData()                   ### saving csv in pandas DataFrame
    print(type(data))
    for i in range(len(data)):          ###  filling table with data from <data>
        current = data.iloc[i]
        current_text = current.text
        current_created_date = current.created_date
        current_created_date = datetime.datetime.strptime(current_created_date, '%Y-%m-%d %H:%M:%S')
        current_rubrics = current.rubrics
        record = posts(text=current_text, created_date=current_created_date, rubrics=current_rubrics)
        db.session.add(record)
    db.session.commit()                 ### commit changes
    file1 = open("check.txt", "a")      ### now we have to write something in check.txt to avoid repeated initialization
    file1.write('1')
    file1.close()                       ### closing connection
    con.close()
    cur.close()
    

@app.route("/")
@app.route("/home")                     ### tracking url's
def index():
    return render_template("index.html")    ### return starter page


@app.route("/posts", methods=['POST', 'GET'])      ### Here we will track to methods
def posts_show():                                  ### GET allows us go to page
    if request.method == "POST":                   ### POST implements searching of string in a database
        target_message = request.form['text']      ### Taking string from form of posts.html
        target_message=target_message.strip()      ### removing extra whitespaces
        articles = posts.query.filter(posts.text.contains(target_message)).order_by(posts.created_date.desc()).limit(20)    ### Saving matching lines and ordering them by created_date
        return render_template("posts.html", articles=articles, target_message=target_message)      ### returning updated page
    else:
        articles = posts.query.order_by(posts.created_date.desc()).limit(20)        ### usual view of latest posts
        return render_template("posts.html", articles=articles)


@app.route("/posts/<int:id>")       ### Also we can check our post in details
def posts_det(id):                  ### with tracking by id
    article = posts.query.get(id)
    return render_template("post_det.html", article=article)


@app.route("/posts/<int:id>/delete")
def posts_delete(id):               ### Delete-function
    article = posts.query.get_or_404(id)    ### getting article by id
    try:
        db.session.delete(article)          ### deleting
        db.session.commit()                 ### commit
        return redirect('/posts')           ### redirect to page with posts
    except:
        return "Error with deleting"        ### or errror +_+ 

@app.route("/posts/<int:id>/update", methods =['POST', 'GET'])
def note_update(id):                        ### we also can edit posts 
    article = posts.query.get(id)              ###  saving current post in article
    if request.method == "POST":               ###  if method is POST function updates current post
        article.text = request.form['text']    ###  
        try:
            db.session.commit()                ### trying to commit
            return redirect('/posts')
        except:
            return "Error"                     ### or returning error

    else:
        return render_template("post_update.html", article=article) ### starter page for this url

@app.route("/about")
def about():
    return render_template("about.html")        ### page about application




if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
