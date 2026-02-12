define config.layers = [ 'master', 'transient', 'topdown', 'screens', 'overlay', 'tooltip' ]    

define narr = Character("Narrator")

label start:
    # show screen mouse_tracker onlayer tooltip
    show screen mouse_tooltip onlayer tooltip

    "Welcome to the AI RPG."
    narr "This is a text-based adventure game where you can explore a world, interact with characters, and embark on quests."
    narr "Before we begin, let's set up your character and choose your story."
    
    # Handles topdown camera zoom in. Should probably be moved.
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
    show screen quest_panel onlayer overlay
    call screen top_down_map(loc) onlayer topdown
    jump world_loop
