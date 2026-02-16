# # Zoomable Map System UI

# init python:
#     def _map_update_zoom(adj_x, adj_y, view_w, view_h):
#         result = map_manager.update_zoom(adj_x, adj_y, view_w, view_h)
#         if result:
#             adj_x.value = result[0]
#             adj_y.value = result[1]
#             renpy.restart_interaction()

#     def _map_center_on(loc, adj_x, adj_y, pad, view_w, view_h):
#         if not loc:
#             return
#         center_x = (loc.map_x + pad) * map_manager.zoom
#         center_y = (loc.map_y + pad) * map_manager.zoom
#         adj_x.value = center_x - view_w / 2
#         adj_y.value = center_y - view_h / 2
#         renpy.restart_interaction()

#     def _map_pan(adj_x, adj_y, dx, dy):
#         adj_x.value = max(0, adj_x.value + dx)
#         adj_y.value = max(0, adj_y.value + dy)
#         renpy.restart_interaction()

#     def _map_edge_arrows(locs, adj_x, adj_y, pad, view_w, view_h, zoom, margin=20):
#         arrows = []
#         for loc in locs:
#             px = int((loc.map_x + pad) * zoom)
#             py = int((loc.map_y + pad) * zoom)
#             sx = px - adj_x.value
#             sy = py - adj_y.value
#             in_view = (sx >= margin and sx <= (view_w - margin) and sy >= margin and sy <= (view_h - margin))
#             if in_view:
#                 continue
#             clamp_x = max(margin, min(view_w - margin, sx))
#             clamp_y = max(margin, min(view_h - margin, sy))
#             dx = sx - view_w / 2
#             dy = sy - view_h / 2
#             if abs(dx) > abs(dy):
#                 arrow = "⬅" if dx < 0 else "➡"
#             else:
#                 arrow = "⬆" if dy < 0 else "⬇"
#             arrows.append((loc, clamp_x, clamp_y, arrow))
#         return arrows

#     def _map_update_mouse():
#         try:
#             mx, my = renpy.get_mouse_pos()
#         except Exception:
#             mx, my = -1, -1
#         store.map_mouse_x = mx
#         store.map_mouse_y = my

#     def _loc_is_descendant(loc, root_id):
#         if not loc or not root_id:
#             return False
#         pid = getattr(loc, "parent_id", None)
#         while pid:
#             if pid == root_id:
#                 return True
#             parent = world.locations.get(pid)
#             pid = getattr(parent, "parent_id", None) if parent else None
#         return False

#     def _map_update_debug(adj_x, adj_y):
#         try:
#             mx, my = renpy.get_mouse_pos()
#         except Exception:
#             mx, my = -1, -1
#         try:
#             pressed = renpy.display.mouse.get_pressed()[0]
#         except Exception:
#             pressed = False
#         store.map_dbg_text = "cam: %.1f, %.1f  zoom: %.2f  target: %.2f\\nmouse: %d, %d  dragging: %s" % (
#             adj_x.value, adj_y.value, map_manager.zoom, map_manager.target_zoom, mx, my, ("yes" if pressed else "no")
#         )

# default quick_travel_on_click = True
# default map_ui_active = False
# default map_dbg_text = ""
# default map_mouse_x = 0
# default map_mouse_y = 0
# default map_local_tip = None
# default phone_map_mode = "overworld"  # overworld | location | areas
# default phone_map_overworld = None
# default phone_map_location = None
# default phone_map_area = None
# image map_grid_bg = Tile(Frame("gui/frame.png"), size=(3000, 3000))

# screen map_browser(view_w=None, view_h=None):
#     modal True
#     zorder 110
    
#     # Store-bound adjustments to track camera
#     default adj_x = ui.adjustment()
#     default adj_y = ui.adjustment()
    
#     # Padding size around the map to allow panning past edges
#     $ PAD = 2000  # Increased for more scroll freedom
#     $ map_w = 3000
#     $ map_h = 3000
#     $ _vw = view_w or config.screen_width
#     $ _vh = view_h or config.screen_height

#     on "show" action [SetVariable("map_ui_active", True), Function(map_manager.center_on_player, adj_x, adj_y, _vw, _vh, PAD), SetField(map_manager, "zoom", 1.0), SetField(map_manager, "target_zoom", 1.0), Function(map_manager.center_on_player, adj_x, adj_y, _vw, _vh, PAD)]
#     on "hide" action [SetVariable("map_ui_active", False)]
    
#     # Background
#     add Solid("#111", xysize=(_vw, _vh))
    
#     # Trigger interaction restart shortly after show for tooltip detection
#     # The delay allows Ren'Py to initialize focus tracking first
#     timer 0.1 action Function(renpy.restart_interaction)
#     timer 0.05 repeat True action Function(_map_update_debug, adj_x, adj_y)
    
#     # Smooth Zoom Timer - Updates zoom with centering
#     timer 0.033 repeat True action Function(_map_update_zoom, adj_x, adj_y, _vw, _vh)
#     # Manual hover tick for reliable tooltips
#     timer 0.05 repeat True action Function(map_manager.update_hover, adj_x, adj_y, PAD, _vw, _vh)
    
#     # 1. Main Map Viewport
#     viewport id "map_vp":
#         xsize _vw
#         ysize _vh
#         draggable True
#         edgescroll (50, 500)
#         xadjustment adj_x
#         yadjustment adj_y
        
#         # Child size includes padding
#         child_size (int((map_w + 2*PAD) * map_manager.zoom), int((map_h + 2*PAD) * map_manager.zoom))
        
#         # The Map Content
#         fixed:
#             # Scaled Background (Centered in padding)
#             add "map_grid_bg":
#                 pos (int(PAD * map_manager.zoom), int(PAD * map_manager.zoom))
#                 at transform:
#                     zoom map_manager.zoom
            
#             # Markers
#             for loc in map_manager.get_visible_markers():
#                 # Apply Padding + Zoom
#                 $ px = int((loc.map_x + PAD) * map_manager.zoom)
#                 $ py = int((loc.map_y + PAD) * map_manager.zoom)
                
#                 $ can_travel = allow_unvisited_travel or loc.visited or (world.current_location_id == loc.id)
#                 $ tooltip_text = (loc.name if can_travel else bracket_label("Undiscovered", "#ff3b3b"))
#                 button:
#                     pos (px, py)
#                     anchor (0.5, 0.5)
#                     tooltip tooltip_text
#                     focus_mask None
#                     if quick_travel_on_click:
#                         action Function(map_manager.travel_to_location, loc)
#                     else:
#                         action Function(map_manager.select_location, loc)
                    
#                     # Visual dependent on type
#                     if loc.ltype == 'world':
#                         text "🌍" size 40 outlines [(2, "#000", 0, 0)]
#                     elif loc.ltype == 'city':
#                         text "🏙️" size 30 outlines [(2, "#000", 0, 0)]
#                     elif loc.ltype == 'structure':
#                         text "🏠" size 24 outlines [(1, "#000", 0, 0)]
#                     elif loc.ltype == 'floor':
#                         text "📍" size 20 outlines [(1, "#000", 0, 0)]
#                     elif loc.ltype == 'room':
#                         text "🚪" size 18 outlines [(1, "#000", 0, 0)]
#                     else:
#                         text "❓" size 20

#                     # Quest Highlight
#                     $ guidance = quest_manager.get_current_guidance()
#                     if guidance and loc.id == guidance.get('location'):
#                         add "images/ui/quest_marker.png" at quest_pulse zoom 0.5 align (0.5, 0.5)

                        
#                     # tooltip set above

#     # 2. Off-screen Arrows (HUD Layer)
#     # We calculate position relative to viewport
#     $ view_w = _vw
#     $ view_h = _vh
    
#     for loc in map_manager.get_visible_markers():
#         $ px = int((loc.map_x + PAD) * map_manager.zoom)
#         $ py = int((loc.map_y + PAD) * map_manager.zoom)
        
#         # Screen coordinates
#         $ sx = px - adj_x.value
#         $ sy = py - adj_y.value
        
#         # Check if off-screen
#         if sx < 0 or sx > view_w or sy < 0 or sy > view_h:
#             # Clamp position to edges with margin
#             $ margin = 50
#             $ arrow_x = max(margin, min(view_w - margin, sx))
#             $ arrow_y = max(margin, min(view_h - margin, sy))
            
#             # Determine direction char (simplified)
#             $ arr_char = "📍"
#             if sx < 0:
#                 $ arr_char = "⬅️"
#             elif sx > view_w:
#                 $ arr_char = "➡️"
#             elif sy < 0:
#                 $ arr_char = "⬆️"
#             elif sy > view_h:
#                 $ arr_char = "⬇️"

#             textbutton "[arr_char]":
#                 pos (arrow_x, arrow_y)
#                 anchor (0.5, 0.5)
#                 # Click jumps to location (centers camera)
#                 # Calculating center adjustment: target_px - screen_w/2
#                 action [SetField(adj_x, "value", px - view_w/2), SetField(adj_y, "value", py - view_h/2)]
#                 background "#0008"
#                 padding (5, 5)
#                 text_size 20

#     # 3. Controls UI (HUD)
#     frame:
#         align (0.0, 0.0)
#         xsize 300
#         ysize _vh
#         background "#000000cc"
#         padding (20, 20)
        
#         vbox:
#             spacing 20
#             text "MAP" size 40 color "#ffd700"
            
#             # Search Input (type to filter)
#             frame:
#                 background "#222"
#                 padding (10, 10)
#                 xfill True
#                 hbox:
#                     spacing 5
#                     text "🔍" color "#888" yalign 0.5
#                     input value FieldInputValue(map_manager, "search_query"):
#                         color "#fff"
#                         size 18
#                         yalign 0.5
#                         length 32
#                     textbutton "✕":
#                         action SetField(map_manager, "search_query", "")
#                         text_size 16
#                         text_color "#888"
#                         yalign 0.5
            
#             # Visible List (Filtered by search)
#             viewport:
#                 ysize 300
#                 scrollbars "vertical"
#                 mousewheel True
#                 vbox:
#                     spacing 5
#                     python:
#                         q = (map_manager.search_query or "").strip().lower()
#                         locs = list(world.locations.values())
#                         if q:
#                             locs = [l for l in locs if (q in (l.name or "").lower()) or (q in (l.description or "").lower())]
#                         locs = sorted(locs, key=lambda l: (l.name or ""))
#                     for loc in locs:
#                         $ can_travel = allow_unvisited_travel or loc.visited or (world.current_location_id == loc.id)
#                         textbutton "[loc.name]":
#                             action [Function(_map_center_on, loc, adj_x, adj_y, PAD, _vw, _vh), Function(map_manager.select_location, loc)]
#                             sensitive can_travel
#                             text_size 16
#                             text_color "#aaa"
#                             text_hover_color "#fff"
#                             xfill True
            
#             null height 20
            
#             # Selection Info
#             if map_manager.selected_structure:
#                 frame:
#                     background "#223"
#                     padding (10, 10)
#                     xfill True
#                     vbox:
#                         text "[map_manager.selected_structure.name]" size 20 color "#aaf"
#                         text "[map_manager.selected_structure.ltype!u]" size 12 color "#666"
                        
#                         null height 10
#                         if map_manager.selected_structure.children:
#                             text "Floors:" size 14 color "#888"
#                             for child in map_manager.selected_structure.children:
#                                 if child.ltype == 'floor':
#                                     textbutton "➜ [child.name]":
#                                         action Function(map_manager.select_location, child)
#                                         text_size 16

#     # 4. Zoom Controls
#     vbox:
#         align (0.95, 0.9)
#         spacing 10
        
#         textbutton "➕":
#             action Function(map_manager.set_zoom, map_manager.target_zoom + 0.5)
#             background "#222"
#             padding (15, 15)
#             text_size 30
#             hover_background "#444"
#             insensitive_background "#111"
#             sensitive (map_manager.target_zoom < 5.0)
#             tooltip "Zoom In"
            
#         text "{:.1f}x".format(map_manager.target_zoom) size 20 color "#fff" xalign 0.5
            
#         textbutton "➖":
#             action Function(map_manager.set_zoom, map_manager.target_zoom - 0.5)
#             background "#222"
#             padding (15, 15)
#             text_size 30
#             hover_background "#444"
#             insensitive_background "#111"
#             sensitive (map_manager.target_zoom > 0.5)
#             tooltip "Zoom Out"

#     # 5. Location Info Popup (overlays everything)
#     if map_manager.selected_location:
#         use location_info_popup(map_manager.selected_location)
    
#     # 7. Tooltip Layer handled by global overlay

# # Embedded minimap for phone (GTA-style: pan/zoom/click)
# screen phone_minimap(view_w=None, view_h=None):
#     modal True
#     zorder 110

#     default adj_x = ui.adjustment()
#     default adj_y = ui.adjustment()

#     $ PAD = 2000
#     $ map_w = 3000
#     $ map_h = 3000
#     $ _vw = view_w or 1200
#     $ _vh = view_h or 700

#     on "show" action [SetVariable("map_ui_active", True), SetField(map_manager, "search_query", ""), SetField(map_manager, "zoom", 1.0), SetField(map_manager, "target_zoom", 1.0), Function(map_manager.center_on_player, adj_x, adj_y, _vw, _vh, PAD)]
#     on "hide" action [SetVariable("map_ui_active", False), SetVariable("map_local_tip", None)]

#     timer 0.01 action Function(map_manager.center_on_player, adj_x, adj_y, _vw, _vh, PAD)
#     timer 0.033 repeat True action Function(_map_update_zoom, adj_x, adj_y, _vw, _vh)
#     timer 0.05 repeat True action Function(map_manager.update_hover, adj_x, adj_y, PAD, _vw, _vh)
#     timer 0.05 repeat True action Function(_map_update_mouse)

#     fixed:
#         xsize _vw
#         ysize _vh
#         add Solid("#0f141b", xysize=(_vw, _vh))

#         viewport id "phone_minimap_vp":
#             xsize _vw
#             ysize _vh
#             draggable True
#             mousewheel True
#             edgescroll (0, 0)
#             xadjustment adj_x
#             yadjustment adj_y
#             child_size (int((map_w + 2*PAD) * map_manager.zoom), int((map_h + 2*PAD) * map_manager.zoom))

#             fixed:
#                 add "map_grid_bg":
#                     pos (int(PAD * map_manager.zoom), int(PAD * map_manager.zoom))
#                     at transform:
#                         zoom map_manager.zoom

#                 $ _all_locs = list(rpgworld_world.locations.values())
#                 for loc in _all_locs:
#                     $ px = int((loc.map_x + PAD) * map_manager.zoom)
#                     $ py = int((loc.map_y + PAD) * map_manager.zoom)
#                     $ can_travel = allow_unvisited_travel or loc.visited or (world.current_location_id == loc.id)
#                     $ tooltip_text = (loc.name if can_travel else bracket_label("Undiscovered", "#ff3b3b"))
#                     button:
#                         pos (px, py)
#                         anchor (0.5, 0.5)
#                         hovered [SetVariable("map_local_tip", tooltip_text), Function(renpy.restart_interaction)]
#                         unhovered [SetVariable("map_local_tip", None), Function(renpy.restart_interaction)]
#                         focus_mask True
#                         action Function(map_manager.select_location, loc)
#                         sensitive True
#                         if loc.ltype == 'world':
#                             text "🌍" size 40 outlines [(2, "#000", 0, 0)]
#                         elif loc.ltype == 'city':
#                             text "🏙️" size 30 outlines [(2, "#000", 0, 0)]
#                         elif loc.ltype == 'structure':
#                             text "🏠" size 24 outlines [(1, "#000", 0, 0)]
#                         elif loc.ltype == 'floor':
#                             text "📍" size 20 outlines [(1, "#000", 0, 0)]
#                         elif loc.ltype == 'room':
#                             text "🚪" size 18 outlines [(1, "#000", 0, 0)]
#                         else:
#                             text "❓" size 20
                        
#                         # Quest Highlight
#                         $ guidance = quest_manager.get_current_guidance()
#                         if guidance and loc.id == guidance.get('location'):
#                             add "images/ui/quest_marker.png" at quest_pulse zoom 0.5 align (0.5, 0.5)


#         # Off-screen clamp indicators (screen space, true position)
#         $ _arrows = _map_edge_arrows(world.locations.values(), adj_x, adj_y, PAD, _vw, _vh, map_manager.zoom)
#         for loc, clamp_x, clamp_y, arrow in _arrows:
#             textbutton "[arrow]":
#                 xpos clamp_x
#                 ypos clamp_y
#                 anchor (0.5, 0.5)
#                 background "#0008"
#                 padding (4, 4)
#                 text_size 18
#                 action Function(_map_center_on, loc, adj_x, adj_y, PAD, _vw, _vh)

#         # Screen-space current location crosshair (clamped)
#         if world.current_location_id in world.locations:
#             $ _cl = world.locations[world.current_location_id]
#             $ cx = int((_cl.map_x + PAD) * map_manager.zoom)
#             $ cy = int((_cl.map_y + PAD) * map_manager.zoom)
#             $ sx = cx - adj_x.value
#             $ sy = cy - adj_y.value
#             $ margin = 16
#             $ clamp_x = max(margin, min(_vw - margin, sx))
#             $ clamp_y = max(margin, min(_vh - margin, sy))
#             add Solid("#ffd700") xpos (clamp_x - 14) ypos (clamp_y - 2) xysize (28, 4)
#             add Solid("#ffd700") xpos (clamp_x - 2) ypos (clamp_y - 14) xysize (4, 28)

#         # Zoom controls (bottom-right)
#         vbox:
#             align (0.97, 0.9)
#             spacing 8
#             textbutton "➕":
#                 action Function(map_manager.set_zoom, map_manager.target_zoom + 0.5)
#                 background "#222"
#                 padding (12, 10)
#                 text_size 26
#                 hover_background "#444"
#                 insensitive_background "#111"
#                 sensitive (map_manager.target_zoom < 5.0)
#             text "{:.1f}x".format(map_manager.target_zoom) size 16 color "#fff" xalign 0.5
#             textbutton "➖":
#                 action Function(map_manager.set_zoom, map_manager.target_zoom - 0.5)
#                 background "#222"
#                 padding (12, 10)
#                 text_size 26
#                 hover_background "#444"
#                 insensitive_background "#111"
#                 sensitive (map_manager.target_zoom > 0.5)

#         # Pan controls (bottom-left)
#         vbox:
#             align (0.03, 0.9)
#             spacing 6
#             textbutton "⬆":
#                 action Function(_map_pan, adj_x, adj_y, 0, -120)
#                 background "#222"
#                 padding (10, 8)
#                 text_size 22
#             hbox:
#                 spacing 6
#                 textbutton "⬅":
#                     action Function(_map_pan, adj_x, adj_y, -120, 0)
#                     background "#222"
#                     padding (10, 8)
#                     text_size 22
#                 textbutton "➡":
#                     action Function(_map_pan, adj_x, adj_y, 120, 0)
#                     background "#222"
#                     padding (10, 8)
#                     text_size 22
#             textbutton "⬇":
#                 action Function(_map_pan, adj_x, adj_y, 0, 120)
#                 background "#222"
#                 padding (10, 8)
#                 text_size 22

#         # Local tooltip overlay
#         if map_local_tip:
#             frame:
#                 background "#000000cc"
#                 padding (8, 6)
#                 xpos (map_mouse_x + 12)
#                 ypos (map_mouse_y + 12)
#                 text "[map_local_tip]" size 14 color "#fff"

