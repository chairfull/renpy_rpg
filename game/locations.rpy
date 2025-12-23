init python:
    pass

# Sample Interaction Labels
label sleep_interaction:
    "You lie down on the bed and rest."
    $ time_manager.sleep()
    jump world_loop

label mirror_interaction:
    "You look at yourself in the mirror. You look like a protagonist."
    jump world_loop

label shopkeeper_talk:
    "Shopkeeper" "Welcome! How can I help you today?"
    "He doesn't have anything for sale yet, but he looks happy to see you."
    $ achievements.unlock("met_shopkeeper")
    jump world_loop
