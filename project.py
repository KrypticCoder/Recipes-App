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

# Connect to Database and create database session
engine = create_engine('sqlite:///recipes.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def decIngredients(ingredients):
    return ingredients.split('@@@@@')

def encIngredients(ingredientsarr):
    return ("@@@@@").join(ingredientsarr)



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
    return render_template('recipe.html', recipe=recipe, items=items)

# Create a new recipe
@app.route('/recipes/new/', methods=['GET', 'POST'])
def newRecipe():
    if request.method == 'POST':
        items = []
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form.getlist('ingredient')
        instructions = request.form['instructions']
        for ingredient in ingredients:
            if ingredient != '':
                items.append(ingredient)
        
        if request.form['submit'] == '+':
                return render_template('newrecipe.html', name=name, description=description, items=items, instructions=instructions)
        elif request.form['submit'] == 'new':
            newRecipe = Recipe(name=name, description=description, ingredients=encIngredients(items), 
                                instructions=instructions)
            session.add(newRecipe)
            session.commit()
            return redirect(url_for('allRecipes'))
    else:
        return render_template('newrecipe.html', name='', description='', items=[], instructions='')


# Edit a recipe
@app.route('/recipes/<int:recipe_id>/edit', methods=['GET', 'POST'])
def editRecipe(recipe_id):
    recipeToEdit = session.query(Recipe).filter_by(id=recipe_id).one()
    
    if request.method == 'POST':
        items = []
        name = request.form['name']
        description = request.form['description']
        ingredients = request.form.getlist('ingredient')
        instructions = request.form['instructions']
        for ingredient in ingredients:
            if ingredient != '':
                items.append(ingredient)    

        if request.form['submit'] == '+':
            return render_template('editrecipe.html', id=recipe_id, name=name, description=description, items=items, instructions=instructions)
        elif request.form['submit'] == 'save':
            recipeToEdit.name = name
            recipeToEdit.description = description
            recipeToEdit.ingredients = encIngredients(items)
            recipeToEdit.instructions = instructions
            session.add(recipeToEdit)
            session.commit()
            return redirect(url_for('allRecipes'))
    else:
        return render_template('editrecipe.html', id=recipe_id, name=recipeToEdit.name, description=recipeToEdit.description, 
                            items=decIngredients(recipeToEdit.ingredients), instructions=recipeToEdit.instructions)

# Delete a recipe
@app.route('/recipes/<int:recipe_id>/delete/', methods=['GET', 'POST'])
def deleteRecipe(recipe_id):
    recipeToDelete = session.query(Recipe).filter_by(id=recipe_id).one()
    if request.method == 'POST':
        print 'delete recipe'
        session.delete(recipeToDelete)
        session.commit()
        return redirect(url_for('allRecipes'))

    else:
        return render_template('deleterecipe.html', recipe=recipeToDelete)



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)