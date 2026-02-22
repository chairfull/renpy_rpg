define config.layers = [ 'topdown', 'master', 'transient', 'screens', 'overlay', 'tooltip' ]    
define narr = Character("Narrator")
#region States
default persistent.lore = set[str]
default persistent.awards = set[str]
default persistent.award_ticks = {}
default quest_state = {}
default flag_state = {}
default quest_hidden = set[str]
default zone_visited = set[str]
default lock_unlocked = set[str]
#endregion
default player = None # Main character reference.
default loop_queue = [] # Labels and screens queued.
default current_scene = None
define null_scene = None

label splashscreen:
    $ renpy.notify("beep boop")
    show screen tooltip_screen onlayer tooltip
    return

label start:
    python:
        global current_scene, null_scene
        from classes import Scene 
        current_scene = Scene()
        null_scene = Scene()
    

    call screen grid_page(4, 3, [
        { "item": None, },
        { "item": None, },
        { "item": None, },
    ])

    "Welcome to the AI RPG."
    narr "This is a text-based adventure game where you can explore a world, interact with characters, and embark on quests."
    narr "Before we begin, let's set up your character and choose your story."
    
    # Handles topdown camera zoom in. Should probably be moved.
    default intro_cinematic_done = False
    
    # Story Selection (skip if a quick-start origin was chosen)
    if preselected_origin_id:
        $ origin = get_quest(preselected_origin_id)
        $ preselected_origin_id = None
        if origin:
            $ finish_story_selection(origin)
            return
    call screen story_select_screen
    
    # After selection, the screen jumps to the intro label.
    # If selection is cancelled, fall back to the main loop.
    jump world_loop_start

label world_loop_start:
    window hide
    $ loc = world.current_location
    show screen quest_panel onlayer overlay
    show screen top_down_screen onlayer topdown
    jump world_loop

label world_loop:
    python:
        if loop_queue:
            qtype, args, kwargs = loop_queue.pop(0)
            if qtype == "label":
                renpy.call(args[0], *args[1:], **kwargs)
            elif qtype == "screen":
                renpy.show_screen(args[0], *args[1:], **kwargs)
            else:
                raise ValueError(f"Unknown loop queue type: {qtype}")
    jump world_loop
