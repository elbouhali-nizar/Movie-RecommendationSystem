import json
import uuid
import pymongo
import random
from json import loads
from functools import wraps
from bson.json_util import dumps
from flask_session import Session
from passlib.hash import pbkdf2_sha256
from flask import Flask, jsonify, render_template, request, session, redirect


app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = b'\xcc^\x91\xea\x17-\xd0W\x03\xa7\xf8J0\xac8\xc5'
Session(app)

# Database
client = pymongo.MongoClient("*********place ur mongoDB url here*********")
db = client.movie_project
movies = db.movies.find()
User_Movie = client['movie_project']['users']




class Movie:
  def start_session(self, mov):
    session['mov'] = mov
    return loads(dumps(mov))
  def Movie_id(self):
    moVie = request.get_json()
    movie0 = json.loads(moVie)
    print(moVie)
    print(movie0["movie_id"])
    idStrMov =str(movie0["movie_id"])
    mov = db.movies.find_one({"id":idStrMov})
    genres = mov['genres']
    print(genres)
    g = genres.split(' ')
    print(g)
    p ={}
    
    movie_list = db.movies.find()
    MovieList = list(movie_list)
    
    for i in range(0,400):

      c = MovieList[i]['genres']
      d = c.split(' ')
      for j in g:
        if len(p) == 8:
          break
        else:
          if g[0] in d and g[1] in d:
              if MovieList[i]['original_title'] not in p and mov['original_title'] != MovieList[i]['original_title']:
                p[MovieList[i]['id']]=MovieList[i]['original_title']
    print(p)
    mov['similarFilms'] = p
    sl = db.users.find_one({ "email": session['user']['email'] })
    if sl:
      print(sl)
      myquery = { "movie": sl['movie']}
      newvalues = { "$set": { "movie": str(sl['movie'])+" ; "+str(mov['original_title']) } }
      
      User_Movie.update_one(myquery, newvalues)
      print('****************************************')
      print('****************************************')
      print("**************INSERTED******************")
      print('****************************************')
      print('****************************************')
      
      print(User_Movie)
    return self.start_session(mov)







  

class User:

  def start_session(self, user):
    del user['password']
    session['logged_in'] = True
    session['user'] = user
    return jsonify(user), 200

  def signup(self):
    print(request.form)

    # Create the user object
    
    user = {
      "_id": uuid.uuid4().hex,
      "name": request.form.get('name'),
      "email": request.form.get('email'),
      "password": request.form.get('password'),
      "movie":"John Carter"
    }

    # Encrypt the password
    user['password'] = pbkdf2_sha256.encrypt(user['password'])
    
    # Check for existing email address
    if db.users.find_one({ "email": user['email'] }):
      return jsonify({ "error": "Email address already in use" }), 400

    if db.users.insert_one(user):
      
      return self.start_session(user)

    return jsonify({ "error": "Signup failed" }), 400
  
  def signout(self):
    session.clear()
    return redirect('/')
  
  def login(self):

    user = db.users.find_one({
      "email": request.form.get('email')
    })
    movMov = db.users.find_one({ "email": user['email'] })
    if user and pbkdf2_sha256.verify(request.form.get('password'), user['password']):
      
      user['movie'] = movMov['movie']
      print("************************************")
      print(user['movie'])
      
      return self.start_session(user)
    
    return jsonify({ "error": "Invalid login credentials" }), 401




# Decorators
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs)
    else:
      return redirect('/')
  
  return wrap

# Routes

@app.route('/user/signup', methods=['POST'])
def signup():
  return User().signup()

@app.route('/MovieInfo/details/', methods=['POST'])
def MovieInfo():
  print('here')
  return Movie().Movie_id()


@app.route('/MovieDetails/')
def MovieDetails():
  print('here mv details')
  return render_template('details.html')



  






@app.route('/user/signout')
def signout():
  return User().signout()

@app.route('/user/login', methods=['POST'])
def login():
  return User().login()

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/dashboard/')
@login_required
def dashboard():
  momomo = db.movies.find()
  MovGenres = list(momomo)
  table_Act_Fant = {}
  table_Ani_Fami = {}
  table_Drama = {}
  table_Scie_Fic = {}
  for i in range(0,3500):
    b=MovGenres[i]['genres']
    l = b.split(' ')
    if len(table_Act_Fant) == 50:
      break
    else:
      if 'Action' in l and 'Fantasy' in l:
        table_Act_Fant[MovGenres[i]['id']] = MovGenres[i]['original_title']
    if len(table_Ani_Fami) == 50:
      break
    else:
      if 'Animation' in l and 'Family' in l:
            table_Ani_Fami[MovGenres[i]['id']] = MovGenres[i]['original_title']
    if len(table_Drama) == 50:
      break 
    else:
      if 'Drama' in l:
            table_Drama[MovGenres[i]['id']] = MovGenres[i]['original_title']
    if len(table_Scie_Fic) == 50:
      break
    else:
      if 'Science' in l and 'Fiction' in l:
            table_Scie_Fic[MovGenres[i]['id']] = MovGenres[i]['original_title']
    
  Movie_genres= {'Action/Fantasy' :table_Act_Fant, 'Animation/Family':table_Ani_Fami,'Drama':table_Drama,'Science-Fiction':table_Scie_Fic}


  sl = db.users.find_one({ "email": session['user']['email'] })
  if sl:
      print(sl)
      myMovie = sl['movie']
      Similar_Mov = myMovie.split(' ; ')
      Selected_rand_Mov = random.choice(Similar_Mov)
      if len(Selected_rand_Mov) == 0 :
        print("no records")
      else:
        sMov = db.movies.find_one({ "original_title":  Selected_rand_Mov})
        print('********************POPO****************')
        sMov_g01 = sMov['genres']
        sMov_genres = sMov_g01.split(' ')
        t={}
        if len(myMovie)==0 or len(sMov['original_title']) == 0:
          t['NO DATA'] ='NO DATA TO BE FOUND'
        else:
          for i in range(100,500):
            b=MovGenres[i]['genres']
            l = b.split(' ')
            if sMov_genres[1] in l:
              t[MovGenres[i]['id']] = MovGenres[i]['original_title']
            if sMov_genres[2] in l:
              t[MovGenres[i]['id']] = MovGenres[i]['original_title']
        M_poplr={}
        for i in range(0,3000):
          Movie_popularity = MovGenres[i]['popularity']
          if float(Movie_popularity) >= 140:
            M_poplr[MovGenres[i]['id']] = MovGenres[i]['original_title']

      return render_template('dashboard.html',movie20=list(Movie_genres.items()),Selected_rand_Mov=t,Similar_Mov=Selected_rand_Mov,M_poplr=M_poplr)

app.run(debug=True)

