init python:
    # Define some locations
    home = Location("home", "Your Home", "A cozy little house.")
    town_square = Location("square", "Town Square", "The heart of the town.")
    shop = Location("shop", "General Store", "A place to buy supplies.")

    # Define some entities
    bed = Entity("Bed", "A comfortable-looking bed.", label="sleep_interaction")
    mirror = Entity("Mirror", "You look great today!", label="mirror_interaction")
    shopkeeper = Entity("Shopkeeper", "A friendly old man.", label="shopkeeper_talk")

    # Set up the world
    rpg_world.add_location(home)
    rpg_world.add_location(town_square)
    rpg_world.add_location(shop)

    # Connect locations
    home.add_connection("square", "Go to Town Square")
    town_square.add_connection("home", "Go Home")
    town_square.add_connection("shop", "Go to Shop")
    shop.add_connection("square", "Leave Shop")

    # Add entities to locations
    home.add_entity(bed)
    home.add_entity(mirror)
    
    # Mayor Character setup
    mayor_npc = RPGCharacter("Mayor")
    mayor_entity = Entity("Mayor", "The leader of our fine town.", label="mayor_talk")
    town_square.add_entity(mayor_entity)
    
    shop.add_entity(shopkeeper)

    # Register Sample Scenes
    intro_scene = Scene("intro", "Arrival in Town", "scene_intro_start", "scene_intro_end")
    scene_manager.add_scene(intro_scene)


# Sample Interaction Labels
label sleep_interaction:
    "You take a short nap and feel refreshed."
    jump world_loop

label mirror_interaction:
    "You look at yourself in the mirror. You look like a protagonist."
    jump world_loop

label mayor_talk:
    $ mayor_npc("Welcome to our town, traveler!")
    $ mayor_npc("I hope you find everything to your liking.")
    jump world_loop

label shopkeeper_talk:
    "Shopkeeper" "Welcome! How can I help you today?"
    "He doesn't have anything for sale yet, but he looks happy to see you."
    $ achievements.unlock("met_shopkeeper")
    jump world_loop

# --- New Scene Implementations ---

label scene_intro_start:
    show screen scene_skip("scene_intro_end")
    "You arrive at the town square, the sun is shining."
    "It's a beautiful day for an adventure."
    hide screen scene_skip
    $ scene_manager.unlock("intro")
    jump world_loop

label scene_intro_end:
    "You skip the intro."
    $ scene_manager.unlock("intro")
    jump world_loop
