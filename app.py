from flask import Flask, render_template, request
import sqlite3
import requests

headers = { 
  "apikey": "5161eff0-ab9f-11ed-a433-4b989759f10e"}



app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    film = request.args.get("film")
    sqliteConnection = sqlite3.connect('shows.db')
    db = sqliteConnection.cursor()
    db.execute(f"""SELECT id, title, year, episodes, rating, group_concat(genre , ', ') FROM shows JOIN ratings on shows.id = ratings.show_id JOIN genres on shows.id = genres.show_id WHERE title LIKE "%{film}%" GROUP BY id LIMIT 100;""")
    results= db.fetchall()
    return render_template("search.html", results=results, film = film)

@app.route("/show/<int:id>")
def show(id):
    sqliteConnection = sqlite3.connect('shows.db')
    db = sqliteConnection.cursor()
    db.execute(f"""SELECT id, title, year, episodes, rating, group_concat(genre ,  ', '), votes FROM shows JOIN ratings on shows.id = ratings.show_id JOIN genres on shows.id = genres.show_id WHERE id = {id} GROUP BY id;""")
    result= db.fetchall()
    result=result[0]
    db.execute(f"SELECT name FROM people WHERE id IN (SELECT person_id FROM writers WHERE show_id = {id})")
    writers=db.fetchall()
    writers=", ".join([w[0] for w in writers])
    if writers == '': writers = "Unknown"
    db.execute(f"SELECT name FROM people WHERE id IN (SELECT person_id FROM stars WHERE show_id = {id})")
    actors=db.fetchall()
    actors=(", ").join([a[0] for a in actors])
    if actors == '': actors = "Unknown"
    params = (
   ("q",result[1]),
   ("tbm","isch"),
    );

    response = requests.get('https://app.zenserp.com/api/v2/search', headers=headers, params=params);
    data = response.json()
    images = data["image_results"]
    url = images[0].get("sourceUrl")
    return render_template("show.html", result = result, writers = writers, actors = actors, url=url)


@app.route("/about")
def about():
    return render_template("about.html")
