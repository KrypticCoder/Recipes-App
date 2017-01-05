from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Recipe, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///recipes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# turn string into array by splitting on '@@@@@'
def decIngredients(ingredients):
    return ingredients.split('@@@@@')

# turn array of strings into one string by joining on '@@@@@'
def encIngredients(ingredientsarr):
    return ("@@@@@").join(ingredientsarr)

# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# Connect with Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Connect with Google
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response 
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# Disconnect from Facebook - Revoke a current user's token and reset their login_session
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

# Disconnect from google  
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('allRecipes'))
    else:
        flash("You were not logged in")
        return redirect(url_for('allRecipes'))

# JSON APIs to view Recipe Information
# View all recipes
@app.route('/recipes/JSON/')
def allRecipesJSON():
    recipes = session.query(Recipe).order_by(asc(Recipe.name))
    return jsonify(recipes=[i.serialize for i in recipes])

# View specific recipe
@app.route('/recipes/<int:recipe_id>/JSON/')
def showRecipeJSON(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    return jsonify(recipe=recipe.serialize)


# Show all recipe names
@app.route('/')
@app.route('/recipes/')
def allRecipes():
    recipes = session.query(Recipe).order_by(asc(Recipe.name))
    return render_template('allrecipes.html', recipes=recipes)

# Show one recipe
@app.route('/recipes/<int:recipe_id>/')
def showRecipe(recipe_id):
    recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    items = decIngredients(recipe.ingredients)
    if 'username' not in login_session or recipe.user_id != login_session['user_id']:
        return render_template('publicrecipe.html', recipe=recipe, items=items)
    else:
        return render_template('recipe.html', recipe=recipe, items=items)

# Create a new recipe
@app.route('/recipes/new/', methods=['GET', 'POST'])
def newRecipe():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        items = []
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form.getlist('ingredient')
        instructions = request.form['instructions']
        for ingredient in ingredients:
            if ingredient != '' and ingredient != '@@@@@':
                items.append(ingredient)
        
        if request.form['submit'] == '+':
                return render_template('newrecipe.html', name=name, description=description, items=items, instructions=instructions)
        elif request.form['submit'] == 'new':
            if request.form['name'] == '':
                flash('Please provide a name for the recipe')
                return render_template('newrecipe.html', description=description, items = items, instructions=instructions)
            else:
                newRecipe = Recipe(name=name, description=description, ingredients=encIngredients(items), 
                                    instructions=instructions, user_id=login_session['user_id'])
                session.add(newRecipe)
                session.commit()
                flash('Recipe successfully created')
                return redirect(url_for('allRecipes'))
    else:
        return render_template('newrecipe.html', name='', description='', items=[], instructions='')


# Edit a recipe
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def editRecipe(recipe_id):
    recipeToEdit = session.query(Recipe).filter_by(id=recipe_id).one()
    
    # user needs to be logged in
    if 'username' not in login_session:
        return redirect('/login')

    # user needs to be the author of the recipe. Error script generated if incorrect user tries to visit this url
    if recipeToEdit.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this recipe');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        items = []
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form.getlist('ingredient')
        instructions = request.form['instructions']
        for ingredient in ingredients:
            if ingredient != '' and ingredient != '@@@@@':
                items.append(ingredient)    

        if request.form['submit'] == '+':
            return render_template('editrecipe.html', id=recipe_id, name=name, description=description, items=items, instructions=instructions)
        elif request.form['submit'] == 'save':
            if request.form['name'] == '':
                flash('Please provide a name for the recipe')
                return render_template('editrecipe.html', id=recipe_id, description=description, items = items, instructions=instructions)
            else:
                recipeToEdit.name = name
                recipeToEdit.description = description
                recipeToEdit.ingredients = encIngredients(items)
                recipeToEdit.instructions = instructions
                session.add(recipeToEdit)
                session.commit()
                flash('recipe successfully edited')
                return redirect(url_for('allRecipes'))
    else:
        return render_template('editrecipe.html', id=recipe_id, name=recipeToEdit.name, description=recipeToEdit.description, 
                            items=decIngredients(recipeToEdit.ingredients), instructions=recipeToEdit.instructions)

# Delete a recipe
@app.route('/recipes/<int:recipe_id>/delete/', methods=['GET', 'POST'])
def deleteRecipe(recipe_id):
    recipeToDelete = session.query(Recipe).filter_by(id=recipe_id).one()

    # user needs to be logged in
    if 'username' not in login_session:
        return redirect('/login')

    # user needs to be the author of the recipe. Error script generated if incorrect user tries to visit this url
    if recipeToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this recipe');}</script><body onload='myFunction()''>"

    if request.method == 'POST':
        print 'delete recipe'
        session.delete(recipeToDelete)
        session.commit()
        flash('recipe successfully deleted')
        return redirect(url_for('allRecipes'))

    else:
        return render_template('deleterecipe.html', recipe=recipeToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)