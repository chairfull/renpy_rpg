# Zoomable Map System UI

image map_grid_bg = Tile(Frame("gui/frame.png"), size=(3000, 3000))

screen map_browser():
    modal True
    zorder 100
    
    # Store-bound adjustments to track camera
    default adj_x = ui.adjustment()
    default adj_y = ui.adjustment()
    
    # Padding size around the map to allow panning past edges
    $ PAD = 1000
    $ map_w = 3000
    $ map_h = 3000
    
    # Background
    add Solid("#111")
    
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
            
            # Search Input (Direct)
            frame:
                background "#222"
                padding (10, 10)
                xfill True
                hbox:
                    spacing 5
                    text "🔍" color "#888" yalign 0.5
                    input value FieldInputValue(map_manager, "search_query"):
                        color "#fff"
                        size 18
                        pixel_width 200
            
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
            action Function(map_manager.set_zoom, map_manager.zoom + 0.5)
            background "#222"
            padding (15, 15)
            text_size 30
            hover_background "#444"
            insensitive_background "#111"
            sensitive (map_manager.zoom < 5.0)
            
        text "[map_manager.zoom]" size 20 color "#fff" xalign 0.5
            
        textbutton "➖":
            action Function(map_manager.set_zoom, map_manager.zoom - 0.5)
            background "#222"
            padding (15, 15)
            text_size 30
            hover_background "#444"
            insensitive_background "#111"
            sensitive (map_manager.zoom > 0.5)

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
