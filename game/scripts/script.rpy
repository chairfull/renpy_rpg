# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")


# The game starts here.

label start:
    "Welcome to the AI RPG."
    # Reload data to ensure latest changes are picked up
    $ instantiate_all()
    
    default intro_cinematic_done = False
    
    # Story Selection (skip if a quick-start origin was chosen)
    if preselected_origin_id:
        $ origin = quest_manager.quests.get(preselected_origin_id)
        $ preselected_origin_id = None
        if origin:
            $ finish_story_selection(origin)
            return
    call screen story_select_screen
    
    # After selection, the screen jumps to the intro label.
    # If selection is cancelled, fall back to the main loop.
    jump world_loop

label world_loop:
    window hide
    $ loc = rpg_world.current_location
    call screen top_down_map(loc)
    jump world_loop
