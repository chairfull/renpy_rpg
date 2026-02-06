# Zoomable Map System UI

init python:
    def _map_update_zoom(adj_x, adj_y, view_w, view_h):
        result = map_manager.update_zoom(adj_x, adj_y, view_w, view_h)
        if result:
            adj_x.value = result[0]
            adj_y.value = result[1]
            renpy.restart_interaction()

image map_grid_bg = Tile(Frame("gui/frame.png"), size=(3000, 3000))

screen map_browser():
    modal True
    zorder 100
    
    # Store-bound adjustments to track camera
    default adj_x = ui.adjustment()
    default adj_y = ui.adjustment()
    
    # Padding size around the map to allow panning past edges
    $ PAD = 2000  # Increased for more scroll freedom
    $ map_w = 3000
    $ map_h = 3000
    $ view_w = config.screen_width
    $ view_h = config.screen_height
    
    # Background
    add Solid("#111")
    
    # Trigger interaction restart shortly after show for tooltip detection
    # The delay allows Ren'Py to initialize focus tracking first
    timer 0.1 action Function(renpy.restart_interaction)
    
    # Center on player when opened
    on "show" action Function(map_manager.center_on_player, adj_x, adj_y, view_w, view_h, PAD)
    
    # Smooth Zoom Timer - Updates zoom with centering
    timer 0.033 repeat True action Function(_map_update_zoom, adj_x, adj_y, view_w, view_h)
    
    # 1. Main Map Viewport
    viewport id "map_vp":
        draggable True
        edgescroll (50, 500)
        xadjustment adj_x
        yadjustment adj_y
        
        # Child size includes padding
        child_size (int((map_w + 2*PAD) * map_manager.zoom), int((map_h + 2*PAD) * map_manager.zoom))
        
        # The Map Content
        fixed:
            # Scaled Background (Centered in padding)
            add "map_grid_bg":
                pos (int(PAD * map_manager.zoom), int(PAD * map_manager.zoom))
                at transform:
                    zoom map_manager.zoom
            
            # Markers
            for loc in map_manager.get_visible_markers():
                # Apply Padding + Zoom
                $ px = int((loc.map_x + PAD) * map_manager.zoom)
                $ py = int((loc.map_y + PAD) * map_manager.zoom)
                
                button:
                    pos (px, py)
                    anchor (0.5, 0.5)
                    action Function(map_manager.select_location, loc)
                    
                    # Visual dependent on type
                    if loc.ltype == 'world':
                        text "🌍" size 40 outlines [(2, "#000", 0, 0)]
                    elif loc.ltype == 'city':
                        text "🏙️" size 30 outlines [(2, "#000", 0, 0)]
                    elif loc.ltype == 'structure':
                        text "🏠" size 24 outlines [(1, "#000", 0, 0)]
                    elif loc.ltype == 'floor':
                        text "📍" size 20 outlines [(1, "#000", 0, 0)]
                    else:
                        text "❓" size 20
                        
                    tooltip loc.name

    # 2. Off-screen Arrows (HUD Layer)
    # We calculate position relative to viewport
    $ view_w = config.screen_width
    $ view_h = config.screen_height
    
    for loc in map_manager.get_visible_markers():
        $ px = int((loc.map_x + PAD) * map_manager.zoom)
        $ py = int((loc.map_y + PAD) * map_manager.zoom)
        
        # Screen coordinates
        $ sx = px - adj_x.value
        $ sy = py - adj_y.value
        
        # Check if off-screen
        if sx < 0 or sx > view_w or sy < 0 or sy > view_h:
            # Clamp position to edges with margin
            $ margin = 50
            $ arrow_x = max(margin, min(view_w - margin, sx))
            $ arrow_y = max(margin, min(view_h - margin, sy))
            
            # Determine direction char (simplified)
            $ arr_char = "📍"
            if sx < 0:
                $ arr_char = "⬅️"
            elif sx > view_w:
                $ arr_char = "➡️"
            elif sy < 0:
                $ arr_char = "⬆️"
            elif sy > view_h:
                $ arr_char = "⬇️"

            textbutton "[arr_char]":
                pos (arrow_x, arrow_y)
                anchor (0.5, 0.5)
                # Click jumps to location (centers camera)
                # Calculating center adjustment: target_px - screen_w/2
                action [SetField(adj_x, "value", px - view_w/2), SetField(adj_y, "value", py - view_h/2)]
                background "#0008"
                padding (5, 5)
                text_size 20

    # 3. Controls UI (HUD)
    frame:
        align (0.0, 0.0)
        xsize 300
        yfill True
        background "#000000cc"
        padding (20, 20)
        
        vbox:
            spacing 20
            text "MAP" size 40 color "#ffd700"
            
            # Search Input (Click to focus, prevents tooltip issues)
            frame:
                background "#222"
                padding (10, 10)
                xfill True
                hbox:
                    spacing 5
                    text "🔍" color "#888" yalign 0.5
                    if map_manager.search_query:
                        text "[map_manager.search_query]" color "#fff" size 18 yalign 0.5
                        textbutton "✕":
                            action SetField(map_manager, "search_query", "")
                            text_size 16
                            text_color "#888"
                            yalign 0.5
                    else:
                        textbutton "Search...":
                            action Function(map_manager.input_search)
                            text_size 18
                            text_color "#666"
                            yalign 0.5
            
            # Visible List (Filtered by search)
            viewport:
                ysize 300
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 5
                    for loc in map_manager.get_visible_markers():
                        textbutton "[loc.name]":
                            action Function(map_manager.select_location, loc)
                            text_size 16
                            text_color "#aaa"
                            text_hover_color "#fff"
                            xfill True
            
            null height 20
            
            # Selection Info
            if map_manager.selected_structure:
                frame:
                    background "#223"
                    padding (10, 10)
                    xfill True
                    vbox:
                        text "[map_manager.selected_structure.name]" size 20 color "#aaf"
                        text "[map_manager.selected_structure.ltype!u]" size 12 color "#666"
                        
                        null height 10
                        if map_manager.selected_structure.children:
                            text "Floors:" size 14 color "#888"
                            for child in map_manager.selected_structure.children:
                                if child.ltype == 'floor':
                                    textbutton "➜ [child.name]":
                                        action Function(map_manager.select_location, child)
                                        text_size 16

    # 4. Zoom Controls
    vbox:
        align (0.95, 0.9)
        spacing 10
        
        textbutton "➕":
            action Function(map_manager.set_zoom, map_manager.target_zoom + 0.5)
            background "#222"
            padding (15, 15)
            text_size 30
            hover_background "#444"
            insensitive_background "#111"
            sensitive (map_manager.target_zoom < 5.0)
            tooltip "Zoom In"
            
        text "{:.1f}x".format(map_manager.target_zoom) size 20 color "#fff" xalign 0.5
            
        textbutton "➖":
            action Function(map_manager.set_zoom, map_manager.target_zoom - 0.5)
            background "#222"
            padding (15, 15)
            text_size 30
            hover_background "#444"
            insensitive_background "#111"
            sensitive (map_manager.target_zoom > 0.5)
            tooltip "Zoom Out"

    # 5. Close Button
    textbutton "EXIT":
        align (0.98, 0.02)
        if renpy.store.__dict__.get("phone_current_app") == "map":
            action SetVariable("phone_current_app", None)
        else:
            action Hide("map_browser")
        background "#444"
        hover_background "#666"
        padding (20, 10)
    
    # 6. Location Info Popup (overlays everything)
    if map_manager.selected_location:
        use location_info_popup(map_manager.selected_location)
    
    # 7. Tooltip Layer - Show as separate screen with high zorder
    on "show" action Show("mouse_tooltip")
    on "hide" action Hide("mouse_tooltip")

# Location Info Popup Screen
screen location_info_popup(loc):
    # Click outside to close - full screen button behind the popup
    button:
        xfill True
        yfill True
        action Function(map_manager.close_location_popup)
        background "#00000066"
    
    # Popup Frame
    frame:
        align (0.5, 0.5)
        xsize 500
        background "#1a1a2e"
        padding (30, 30)
        
        vbox:
            spacing 15
            
            # Header
            hbox:
                xfill True
                text "[loc.name]" size 28 color "#ffd700" bold True
                textbutton "✕":
                    align (1.0, 0.0)
                    action Function(map_manager.close_location_popup)
                    text_size 24
                    text_color "#888"
                    text_hover_color "#fff"
            
            # Type Badge
            frame:
                background "#333"
                padding (10, 5)
                text "[loc.ltype!u]" size 14 color "#aaa"
            
            null height 5
            
            # Description
            text "[loc.description]" size 18 color "#ccc" text_align 0.0
            
            null height 15
            
            # Travel Button
            textbutton "🚶 TRAVEL HERE":
                xfill True
                action Function(map_manager.travel_to_location, loc)
                background "#2d5a27"
                hover_background "#3d7a37"
                padding (20, 15)
                text_size 22
                text_color "#fff"
                text_xalign 0.5

label map_search_input_label:
    $ q = renpy.input("Search map:", default=map_manager.search_query, length=20)
    $ map_manager.search(q)
    return

