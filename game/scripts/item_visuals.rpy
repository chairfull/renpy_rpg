
# Define a transform for item popup that bounces in from the bottom
transform item_popup_bounce:
    on show:
        yalign 1.5
        pause 0.1
        easein_back 0.6 yalign 0.25
    on hide:
        easeout_back 0.6 yalign 1.5

label show_item(item_id):
    python:
        # Resolve item and update globals used by the screen
        item = item_manager.get(item_id)
        if item:
            store.item_inspect_image = get_item_icon(item)
            store.item_inspect_title = item.name
    
    # Show the screen
    show screen item_inspect_image
    return

label hide_item(item_id=None):
    # Hide the screen
    hide screen item_inspect_image
    
    python:
        store.item_inspect_image = None
        store.item_inspect_title = ""
    return
