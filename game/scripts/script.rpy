define config.layers = [ 'master', 'transient', 'topdown', 'screens', 'overlay', 'tooltip' ]    

define narr = Character("Narrator")

label start:
    # show screen mouse_tracker onlayer tooltip
    show screen mouse_tooltip onlayer tooltip

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
    $ loc = world.current_location
    show screen quest_panel onlayer overlay
    call screen top_down_map(loc) onlayer topdown
    jump world_loop

init -5 python:
    import math

    class FlowQueueManager(object):
        def __init__(self):
            self.queue = []
            self.active_label = None

        def queue_label(self, label_name):
            if label_name and renpy.has_label(label_name):
                self.queue.append(label_name)

        def process(self):
            if not self.active_label and self.queue:
                self.active_label = self.queue.pop(0)
                renpy.call_in_new_context(self.active_label)
                self.active_label = None

default flow_queue = FlowQueueManager()