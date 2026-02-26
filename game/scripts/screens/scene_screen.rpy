# init python:
#     from renpy.uguu import GL_FUNC_ADD, GL_FUNC_SUBTRACT, GL_ONE, GL_ONE_MINUS_SRC_ALPHA, GL_MIN, GL_ONE_MINUS_DST_COLOR, GL_MAX, GL_ZERO
#     config.gl_blend_func["screen"] = (GL_FUNC_ADD, GL_ONE_MINUS_DST_COLOR, GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE)
#     config.gl_blend_func["lighten"] = (GL_MAX, GL_ONE, GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
#     config.gl_blend_func["darken"] = (GL_MIN, GL_ONE, GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
#     config.gl_blend_func["erase"] = (GL_FUNC_ADD, GL_ZERO, GL_ONE, GL_FUNC_ADD, GL_ZERO, GL_ONE_MINUS_SRC_ALPHA)
#     config.gl_blend_func["sub"] = (GL_FUNC_SUBTRACT, GL_ONE, GL_ONE, GL_FUNC_ADD, GL_ONE, GL_ONE_MINUS_SRC_ALPHA)
#     config.gl_blend_func["sub_better"] = (GL_FUNC_SUBTRACT, GL_ONE, GL_ONE, GL_FUNC_SUBTRACT, GL_ONE, GL_ONE)

# init python:
#     import pygame_sdl2 as pg

#     class DarknessLayer(renpy.Displayable):
#         def get_light_surface(self, light):
#             if not hasattr(light, "_light_surf"):
#                 raw = pg.image.load(renpy.loader.load(light.image))
#                 d = light.radius * 2
#                 scaled = pg.transform.scale(raw.convert_alpha(), (d, d))
#                 light._light_surf = scaled
#             return light._light_surf
        
#         def render(self, width, height, st, at):
#             mx, my = renpy.get_mouse_pos()

#             # Black overlay at full opacity
#             overlay = renpy.display.pgrender.surface((width, height), True)
#             overlay.fill((0, 0, 0, 255))

#             # Subtract the light's alpha channel from the overlay,
#             # punching a transparent hole where the light is brightest
#             for light in renpy.store.current_scene.lights:
#                 lx, _, lz = light.position
#                 overlay.blit(self.get_light_surface(light), (lx - light.radius, lz - light.radius), special_flags=pg.BLEND_RGBA_SUB)

#             # Convert the pygame surface into a Ren'Py render
#             tex = renpy.display.draw.load_texture(overlay, transient=True)
#             rv = renpy.Render(width, height)
#             rv.blit(tex, (0, 0))

#             renpy.redraw(self, 0)
#             return rv

#         def visit(self):
#             return []  # no child Ren'Py displayables to visit (raw pygame surface)

#     class LightingLayer(renpy.Displayable):
#         def get_light_surface(self, light):
#             if not hasattr(light, "_light_surf"):
#                 raw = pg.image.load(renpy.loader.load(light.image))
#                 d = light.radius * 2
#                 light._light_surf = pg.transform.scale(raw.convert_alpha(), (d, d))
#             return light._light_surf

#         def render(self, width, height, st, at):
#             r = renpy.Render(width, height)

#             for light in renpy.store.current_scene.lights:
#                 lx, _, lz = light.position
#                 d = light.radius * 2

#                 t = Transform(
#                     renpy.display.im.Scale(light.image, d, d),
#                     alpha=light.energy,
#                     matrixcolor=TintMatrix(light.color)
#                 )
#                 light_r = renpy.render(t, d, d, st, at)
#                 r.blit(light_r, (lx - light.radius, lz - light.radius))

#             renpy.redraw(self, 0)
#             return r

#         def visit(self):
#             return []

# define darkness = DarknessLayer()
# define lighting = LightingLayer()

transform updater_transform(ent):
    subpixel True
    function ent._update_transform

screen scene_screen():
    """Updates and renders a Scene object and it's children."""
    modal True
    zorder 10
    # timer 0.1 action Function(renpy.restart_interaction) repeat True
    $ scene = current_scene or null_scene
    $ camera = scene.camera
    
    # Initialise.
    on "show" action Function(scene._ready)
    
    # Zoom Controls.
    key "K_PLUS" action Function(camera._zoom, 0.1)
    key "K_EQUALS" action Function(camera._zoom, 0.1)
    key "K_MINUS" action Function(camera._zoom, -0.1)
    key "mousedown_4" action Function(camera._zoom, 0.1)
    key "mousedown_5" action Function(camera._zoom, -0.1)
    # # Debug.
    # key "c" action Function(scene.snap_camera)
    # key "h" action Function(scene.toggle_debug)
    
    # Update Loop.
    # timer 0.03 action Function(scene._process, scene.update_dt) repeat True

    fixed at updater_transform(scene):
        xsize config.screen_width
        ysize config.screen_height
        
        fixed:
            xfill True
            yfill True
            
            # Non-interactive background elements.
            for entity in scene.bg:
                add entity.image at updater_transform(entity):
                    matrixcolor entity.matrixcolor
            
            # Detect when clicking nothing.
            button:
                area (0, 0, config.screen_width, config.screen_height)
                hovered Function(scene._hovered, None)
                action Function(scene._clicked, None)
                alternate Function(scene._clicked, None, True)
                background None
            
            # Interactive objects.
            for entity in scene.children:
                imagebutton at updater_transform(entity):
                    hovered Function(scene._hovered, entity)
                    action Function(scene._clicked, entity)
                    alternate Function(scene._clicked, entity, True)
                    idle entity.image
                    tooltip entity.tooltip
                    focus_mask True
                    background None
                # text "[entity.transform.pos] [entity.transform.zoom]" at _entity_transform(entity)
    
    add lighting:
        blend "multiply"
    
    text "[scene.msg]":
        size 64
        color "#ffffff"

    fixed at updater_transform(scene.cursor):
        if scene.hovering == None:
            add Solid("#ff69b4") xsize 16 ysize 16