# Recipes App

## Description
Web application where users can read and post their favorite recipes. Users can go to the homepage at 'localhost:8000/' or to 'localhost:8000/recipes' and view a list of recipe names. The content of a particular recipe is displayed by clicking on a recipe name. Users can log in through 3rd party oauth system using Facebook or Google. If a user is logged in, they can create, edit, and delete their own recipes.

## Requirements
- [Python 3](https://www.python.org/)

## Setup
1. Download or clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. Install all the required modules by typing `pip install` and then each of the following:
	- flask
	- sqlalchemy
	- oauth2client
	- requests


## Usage 
- Initialize database: `python database_setup.py`
- Fill up database: `python database_run.py`
- Run project: `python project.py`
- View project: visit `localhost:8000/`

![Created New Recipe](http://i.imgur.com/5PjFFCd.png)

## API Endpoints
|Request | What you get |
|--------------|:-----------:|
| /recipes | Show all recipes|
| /recipes/new | Create new recipe|
| /recipes/<int:recipe_id>/edit | Edit recipe |
| /recipes/<int:recipe_id>/delete | Delete recipe |
| /recipes/JSON | JSON for all recipes |
| /recipes/<int:recipe_id>/JSON/ | JSON for a particular recipe |
| /login | Login to Facebook or Google |
| /fbconnect | Connect with Facebook |
| /gconnect | Connect with Google |
| /disconnect | Disconnect based on provider |
| /fbdisconnect | Disconnect with Facebook |
| /gdisconnect | Disconnect with Google |
