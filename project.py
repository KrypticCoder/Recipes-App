from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Recipe, User, Ingredient
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

# Connect to Database and create database session
engine = create_engine('sqlite:///recipeslist.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# show all recipes 
@app.route('/')
@app.route('/recipes')
def allRecipes():
    recipes = session.query(Recipe).order_by(asc(Recipe.name))
    return render_template('allrecipes.html', recipes=recipes)

@app.route('/recipes/<int:recipe_id>/')
def showRecipe(recipe_id):
    # recipe = session.query(Recipe).filter_by(id=recipe_id).one()
    # ingredients = session.query(Ingredient).filter_by(id=recipe_id)


@app.route('/recipes/new/')
def newRecipe():
    pass








if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)