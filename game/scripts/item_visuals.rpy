
# Item Visual Popups

# Define a 'back' transition that uses overshoot easing
# Since Ren'Py doesn't have a built-in 'back' transition, we define it here.
# We'll use a screen-compatible effect.
define back = MoveTransition(0.6, enter_time_warp=_warper.easein_back, leave_time_warp=_warper.easeout_back)

label show_item(item_id):
    python:
        # Resolve item and update globals used by the screen
        item = item_manager.get(item_id)
        if item:
            store.item_inspect_image = get_item_icon(item)
            store.item_inspect_title = item.name
    
    # Show the screen with the transition
    show screen item_inspect_image
    with back
    return

label hide_item(item_id=None):
    # Hide the screen with the transition
    hide screen item_inspect_image
    with back
    
    python:
        store.item_inspect_image = None
        store.item_inspect_title = ""
    return
