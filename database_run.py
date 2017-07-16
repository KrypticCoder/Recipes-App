from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Recipe  # Existing database
from sqlalchemy.sql import *



def parseIngredients(ingredients):
    ingredientsarr = ingredients.split('@@@@@')
    return ingredientsarr

engine = create_engine('sqlite:///recipes.db')  # Lets program know which database 
                                                    # engine we want to communicate with

Base.metadata.bind = engine # Connects class connections to tables in db

DBSession = sessionmaker(bind = engine)     # Establishes link of communication 
                                            # b/w code executions and engine

'''
In order to perform CRUD on our db, SQLAlchemy executes operations via 
interface called session. Session allows us to write down all commands 
we want to execute but not send them to database until we call session.commit
'''

session = DBSession() # Staging area for all objects loaded into database session object 

##### Delete all values #####
all_recipes = session.query(Recipe).all()
for recipe in all_recipes:
    session.delete(recipe)
session.commit()


##### INSERTING #####
print("Inserting values into db...")

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

Recipe1 = Recipe(name="Chicken Ropa Vieja", description="Traditionally, ropa vieja or carne desmechada is made with beef, but this recipe swaps in chicken for a healthier (but just as delicious!) variation. Served over rice with tajadas de maduro, this Chicken Ropa Vieja is an excellent dish that the whole family will love",
                ingredients="4 chicken breasts@@@@@garlic@@@@@pepper@@@@@onion",
                instructions="Make the chicken: In a pot, place the chicken, onion, green pepper, carrot, and garlic. Add water to cover the chicken, add salt, pepper and cook over medium heat for about 30 minutes or until the chicken is cooked. \
                    Measure and strain 1 cup of the liquid used to cook the chicken and set aside. \
                    Remove the chicken from the pot, let cool, and shred with a fork or your hands. \
                    Make the sofrito: In a large sauce pan, heat the oil over medium heat. Add garlic, onions, and red pepper. Cook about 5 to 7 minutes, or until tender. \
                    Add the cooked and shredded chicken, reserved broth, tomato sauce, tomato paste, cumin, salt, pepper and capers. \
                    Cover and cook on low for about 10 minutes, adding more broth and seasoning if needed, stirring occasionally. Serve warm.",
                user_id = User1.id)
session.add(Recipe1) 
session.commit()

# ingredient1a = Ingredient(content='4 chicken breasts', recipe_id = Recipe1.id, user_id=User1.id)
# ingredient1b = Ingredient(content='garlic', recipe_id = Recipe1.id, user_id=User1.id)
# ingredient1c = Ingredient(content='pepper', recipe_id = Recipe1.id, user_id=User1.id)
# ingredient1d = Ingredient(content='onion', recipe_id = Recipe1.id, user_id=User1.id)
# session.add(ingredient1a)
# session.add(ingredient1b)
# session.add(ingredient1c)
# session.add(ingredient1d)
# session.commit()

print('\n')

##### QUERYING ##### 
print('Querying db...')

all_recipes = session.query(Recipe).all()

for recipe in all_recipes:
    print('name: ' + recipe.name)
    print('description: ' + recipe.description)
    print ('ingredients: ')
    for item in parseIngredients(recipe.ingredients):
        print(item)
    print('instructions: ' + recipe.instructions)

print('\n')

# ###### UPDATING #####
# print('Updating values in db...')
# recipe = session.query(Recipe).one()
# print(recipe.name)
# print(recipe.description)
# recipe.description = "My favorite recipe"
# print('recipe description changed to: ' + recipe.description)
# session.add(recipe)
# session.commit()

# print('\n')

# ##### DELETING #####
# print('Deleting values from db... ')

# for recipe in all_recipes:
#     session.delete(recipe)
# session.commit()


# # Database should be empty now
# all_recipes = session.query(Recipe).all()
# if len(all_recipes) == 0:
#     print("Restaurant table is empty")
# else:
#     print("Restaurant table still holds tuples")
#     for recipe in all_recipes:
#         print(recipe.name)








