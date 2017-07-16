# Recipes App

## Description
Web application where users can read and post their favorite recipes. Users can go to the homepage at 'localhost:8000/' or to 'localhost:8000/recipes' and view a list of recipe names. The content of a particular recipe is displayed by clicking on a recipe name. Users can log in through 3rd party oauth system using Facebook or Google. If a user is logged in, they can create, edit, and delete their own recipes.

## Requirements
- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)
- [Python ~2.7](https://www.python.org/)

## Setup
1. Download or clone the [fullstack-nanodegree-vm repository](https://github.com/udacity/fullstack-nanodegree-vm).

2. On your local system, locate the *vagrant* folder and inside it copy the contents of this current repository, by either downloading it or cloning it. 

## Usage 
- Launch Vagrant VM from inside *vagrant* folder: `vagrant up`
- Login to Vagrant: `vagrant ssh`
- Move to catalog folder: `cd /vagrant/catalog`
- Initialize database: `python database_setup.py`
- Fill up database: `python database_run.py`
- Run project: `python project.py`
- View project: visit `localhost:8000/`

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
