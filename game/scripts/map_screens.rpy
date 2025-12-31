# Zoomable Map System UI

image map_grid_bg = Tile(Frame("gui/frame.png"), size=(3000, 3000))

screen map_browser():
    modal True
    zorder 100
    
    # Background
    add Solid("#111")
    
    # 1. Main Map Viewport
    # We use a fixed logical size of 3000x3000 for the world map
    viewport id "map_vp":
        draggable True
        edgescroll (50, 500)
        # Dynamic child size based on zoom
        child_size (int(3000 * map_manager.zoom), int(3000 * map_manager.zoom))
        xfill True
        yfill True
        
        # The Map Content
        fixed:
            # Scaled Background
            add "map_grid_bg":
                at transform:
                    zoom map_manager.zoom
            
            # Markers
            for loc in map_manager.get_visible_markers():
                $ px = int(loc.map_x * map_manager.zoom)
                $ py = int(loc.map_y * map_manager.zoom)
                
                button:
                    pos (px, py)
                    anchor (0.5, 0.5)
                    action Function(map_manager.select_location, loc)
                    
                    # Visual dependent on type
                    if loc.ltype == 'world':
                        text "🌍" size 40
                    elif loc.ltype == 'city':
                        text "🏙️" size 30
                    elif loc.ltype == 'structure':
                        text "🏠" size 24
                    elif loc.ltype == 'floor':
                        text "📍" size 20
                    else:
                        text "❓" size 20
                        
                    # Label on hover
                    tooltip loc.name

    # 2. Controls UI (HUD)
    frame:
        align (0.0, 0.0)
        xsize 300
        yfill True
        background "#000000cc"
        padding (20, 20)
        
        vbox:
            spacing 20
            text "WORLD MAP" size 40 color "#ffd700"
            
            # Search
            hbox:
                spacing 10
                textbutton "🔍":
                    action Function(map_manager.input_search)
                text "[map_manager.search_query]" color "#ccc" size 18 yalign 0.5
            
            null height 20
            
            # Selection Info
            if map_manager.selected_structure:
                text "[map_manager.selected_structure.name]" size 24 color "#aaf"
                text "Floors:" size 18 color "#888"
                
                # Floor Selector
                viewport:
                    height 200
                    scrollbars "vertical"
                    vbox:
                        for child in map_manager.selected_structure.children:
                            if child.ltype == 'floor':
                                textbutton "[child.name]":
                                    action Function(map_manager.select_location, child)
                                    text_size 16
            
            else:
                text "Select a location..." size 18 italic True color "#666"

    # 3. Zoom Controls
    vbox:
        align (0.95, 0.9)
        spacing 10
        
        textbutton "➕":
            action Function(map_manager.set_zoom, map_manager.zoom + 0.5)
            background "#222"
            padding (15, 15)
            text_size 30
            
        text "[map_manager.zoom]" size 20 color "#fff" xalign 0.5
            
        textbutton "➖":
            action Function(map_manager.set_zoom, map_manager.zoom - 0.5)
            background "#222"
            padding (15, 15)
            text_size 30

    # 4. Close Button
    textbutton "EXIT":
        align (0.98, 0.02)
        if renpy.store.__dict__.get("phone_current_app") == "map":
            action SetVariable("phone_current_app", None)
        else:
            action Hide("map_browser")
        background "#444"
        padding (20, 10)

label map_search_input_label:
    $ q = renpy.input("Search map (e.g. 'tower'):", default=map_manager.search_query)
    $ map_manager.search(q or "")
    return
