screen scene_screen():
    """Updates and renders a Scene object and it's children."""
    modal True
    $ scene = current_scene or null_scene
    zorder 10
    
    # Initialise.
    on "show" action [Function(scene._ready)]
    
    # Zoom Controls.
    # key "K_PLUS" action Function(scene.zoom, 0.1)
    # key "K_EQUALS" action Function(scene.zoom, 0.1)
    # key "K_MINUS" action Function(scene.zoom, -0.1)
    # key "mousedown_4" action Function(scene.zoom, 0.1)
    # key "mousedown_5" action Function(scene.zoom, -0.1)
    # # Debug.
    # key "c" action Function(scene.snap_camera)
    # key "h" action Function(scene.toggle_debug)
    
    # Update Loop.
    timer scene.update_dt action Function(scene._process, scene.update_dt) repeat True
    
    text "Ass":
        size 64
        color "#ffffff"

    # fixed:
    #     xsize config.screen_width
    #     ysize config.screen_height
        
    #     fixed:
    #         xfill True
    #         yfill True
            
    #         # Non-interactive background elements.
    #         for entity in scene.bg:
    #             $ ex, ey = camera.world_to_screen(entity.position)
    #             add entity.image:
    #                 pos (ex, ez)
            
    #         # Detect when clicking nothing.
    #         button:
    #             area (0, 0, config.screen_width, config.screen_height)
    #             action Function(scene._clicked, None)
    #             alternate Function(scene._clicked, None, True)
    #             background None
            
    #         # Interactive objects.
    #         for entity in scene.children:
    #             $ epos = camera.world_to_screen(entity.position)
    #             if not camera.position_in_view(epos):
    #                 continue
    #             imagebutton at entity.transform:
    #                 pos epos.xz_int
    #                 hovered Function(entity._hovered)
    #                 unhovered Function(entity._unhovered)
    #                 action Function(scene._clicked, entity)
    #                 alternate Function(scene._clicked, entity, True)
    #                 tooltip entity.tooltip
    #                 focus_mask None
    #                 background None

    # $ zone = player.zone
    # frame:
    #     align (0.5, 0.02)
    #     background "#00000088"
    #     padding (20, 8)
    #     textbutton "[zone.name]":
    #         action [Function(meta_menu.open, "locations")]
    #         text_size 28
    #         text_color "#ffffff"
    #         text_hover_color "#ffd700"
    #         background None
    #         hover_background None
    
    # frame:
    #     align (0.18, 0.02)
    #     background "#00000088"
    #     padding (12, 10)
    #     vbox:
    #         spacing 6
    #         text "Time: [world_time.time_string]" size 18 color "#ffd700"
    #         hbox:
    #             spacing 6
    #             textbutton "+15m" action Function(world_time.advance, 15) text_size 14
    #             textbutton "+1h" action Function(world_time.advance, 60) text_size 14
    #             text "[world_time.time_of_day]" size 14 color "#ccc"
    #         text "Here now:" size 14 color "#aaa"
    #         vbox:
    #             spacing 2
    #             for c in zone.characters:
    #                 $ nxt_time, nxt_loc = c.next_schedule_entry()
    #                 hbox:
    #                     spacing 6
    #                     text c.name size 14 color "#fff"
    #                     if nxt_time and nxt_loc:
    #                         text f"→ {nxt_loc} @ {nxt_time}" size 12 color "#777"
    
    # frame:
    #     align (0.02, 0.98)
    #     background "#000a"
    #     padding (10, 10)
    #     hbox:
    #         spacing 10
    #         textbutton "DEV" action Show("dev_mode_screen") text_size 14 text_color "#ff3333"
    
    # use meta_menu_screen

    # Debug draw cursor.
    add Solid("#ff69b4") pos scene.smoothed_mouse.xz_int xsize 16 ysize 16

# label char_interaction_show:
#     $ char = getattr(store, '_interact_target_char', None)
#     if not char:
#         return
#     $ char_interaction_state = "menu"
#     $ char_interaction_pending_label = None
#     $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)

#     # show character on right
#     if char.base_image:
#         show expression Transform(char.base_image, xzoom=-1) as char_right at right
#         with dissolve

#     # move player in from left
#     if character.base_image:
#         show expression character.base_image as char_left at left
#         with moveinleft

#     jump char_interaction_loop

# label char_interaction_loop:
#     $ char = getattr(store, '_interact_target_char', None)
#     if not char:
#         jump char_interaction_end
#     $ char_interaction_state = "menu"
#     $ char_interaction_pending_label = None
#     $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
#     while True:
#         $ renpy.pause(0.05)
#         if not getattr(store, '_interact_target_char', None):
#             $ char_interaction_state = "exit"
#         if char_interaction_state == "exit":
#             jump char_interaction_end
#         if char_interaction_pending_label:
#             $ _lbl = char_interaction_pending_label
#             $ char_interaction_pending_label = None
#             $ renpy.hide_screen("char_interaction_menu")
#             $ renpy.with_statement(Dissolve(0.2))
#             if renpy.has_label(_lbl):
#                 call expression _lbl from _call_npc_label_wrapper
#             $ renpy.show_screen("char_interaction_menu", char, show_preview=False, show_backdrop=False)
#             $ renpy.with_statement(Dissolve(0.2))
#             $ char_interaction_state = "menu"

# label _char_interaction_run_pending:
#     $ _lbl = char_interaction_pending_label
#     $ char_interaction_pending_label = None
#     if not _lbl:
#         return
#     $ _char = getattr(store, '_interact_target_char', None)
#     if not _char:
#         return
#     $ renpy.hide_screen("char_interaction_menu")
#     $ renpy.with_statement(Dissolve(0.2))
#     if renpy.has_label(_lbl):
#         call expression _lbl
#     $ renpy.show_screen("char_interaction_menu", _char, show_preview=False, show_backdrop=False)
#     $ renpy.with_statement(Dissolve(0.2))
#     return

# label char_interaction_end:
#     hide screen char_interaction_menu
#     if character.base_image:
#         show expression Transform(character.base_image, xzoom=-1) as char_left at offscreenleft with moveoutleft
#     hide char_right with dissolve
#     hide char_left
#     $ _interact_target_char = None
#     return
