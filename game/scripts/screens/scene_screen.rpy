init python:
    class SceneLightingLayer(renpy.Displayable):
        """
        Black = full darkness, color = illumination.
        """
        def _get_surface(self, light, zoom):
            key = (light.radius, light.energy, light.color, zoom)
            if getattr(light, "_light_surf_key", None) != key:
                r = int(light.radius * zoom)
                d = r * 2
                raw = pg.image.load(renpy.loader.load(light.image))
                surf = pg.transform.scale(raw.convert_alpha(), (d, d))

                # Bake color tint into RGB only.
                cr, cg, cb = light.color[:3]
                tint = pg.Surface((d, d), pg.SRCALPHA)
                tint.fill((cr, cg, cb, 255))
                surf.blit(tint, (0, 0), special_flags=pg.BLEND_RGB_MULT)

                # Bake energy into alpha only.
                energy_surf = pg.Surface((d, d), pg.SRCALPHA)
                energy_surf.fill((255, 255, 255, int(light.energy * 255)))
                surf.blit(energy_surf, (0, 0), special_flags=pg.BLEND_RGBA_MULT)

                light._light_surf = surf
                light._light_surf_key = key
            return light._light_surf

        def render(self, width, height, st, at):
            scene  = renpy.store.current_scene
            camera = scene.camera

            # Hash the state — only rebuild if something moved or changed.
            state = (camera.zoom, camera.position, tuple(
                (id(l), l.position.xz)
                for l in scene.lights.values()
            ))

            if not hasattr(self, "_last_state") or self._last_state != state:

                # Black = darkness; lights will carve out and tint illuminated areas.
                overlay = renpy.display.pgrender.surface((width, height), True)
                overlay.fill((0, 0, 0, 255))

                for light in scene.lights.values():
                    surf = self._get_surface(light, camera.zoom)
                    r = int(light.radius * camera.zoom)
                    sx, sz = camera.to_screen(light.position).xz_int
                    overlay.blit(surf, (sx - r, sz - r))
                
                self._cached_tex = renpy.display.draw.load_texture(overlay, transient=True)
                self._last_state = state

            # tex = renpy.display.draw.load_texture(overlay, transient=True)
            rv  = renpy.Render(width, height)
            rv.blit(self._cached_tex, (0, 0))
            renpy.redraw(self, 1/24) # 25 frames per second seems an okay tradeoff
            return rv

        def visit(self):
            return []
    
    class SceneDebugLayer(renpy.Displayable):
        def render(self, width, height, st, at):
            scene  = renpy.store.current_scene
            camera = scene.camera

            surf = renpy.display.pgrender.surface((width, height), True)

            for k, v in scene.debug.items():
                clr = getattr(v, "debug_color", "#ff00ff")
                wid = getattr(v, "debug_width", 1)
                # Draw point list
                if isinstance(v, PointList):
                    points = [camera.to_screen(x).xz_int for x in v.points]
                    for i in range(0, len(points)-1):
                        pg.draw.line(surf, clr, points[i], points[i+1], wid)
                    if v.closed:
                        pg.draw.line(surf, clr, points[0], points[-1], wid)
                # Draw circle
                elif isinstance(v, Sphere):
                    points = [camera.to_screen(x).xz_int for x in v.get_circle(32)]
                    for i in range(0, len(points)):
                        pg.draw.line(surf, clr, points[i-1], points[i], wid)
                # Draw point
                elif isinstance(v, Point):
                    px, pz = v.xz_int
                    pg.draw.circle(surf, clr, px, pz, 16)
            
            tex = renpy.display.draw.load_texture(surf, transient=True)
            rv  = renpy.Render(width, height)
            rv.blit(tex, (0, 0))
            renpy.redraw(self, 1/40)
            return rv

        def visit(self):
            return []

define scene_lighting_layer = SceneLightingLayer()
define scene_debug_layer = SceneDebugLayer()

transform updater_transform(ent):
    subpixel True
    function ent._update_transform

transform scene_hovered:
    subpixel True
    alpha 0.0
    on show:
        block:
            ease 0.1 alpha 1.0
        block:
            ease 0.5 alpha 0.5
            ease 0.25 alpha 1.0
            repeat
    on hide:
        ease 0.2 alpha 0.0

screen scene_screen():
    """Updates and renders a Scene object and it's children."""
    modal True
    zorder 10
    # timer 0.1 action Function(renpy.restart_interaction) repeat True
    default hover_entity = None
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
            for bg_entity in scene.bg.values():
                add bg_entity.image at updater_transform(bg_entity):
                    matrixcolor bg_entity.matrixcolor
            
            # Detect when clicking nothing.
            button:
                area (0, 0, config.screen_width, config.screen_height)
                hovered Function(scene._hovered, None)
                action Function(scene._clicked, None)
                alternate Function(scene._clicked, None, True)
                background None
            
            # Interactive objects.
            for entity in scene.children.values():
                imagebutton at updater_transform(entity):
                    hovered Function(scene._hovered, entity)
                    unhovered NullAction()
                    action Function(scene._clicked, entity)
                    alternate Function(scene._clicked, entity, True)
                    idle entity.image
                    tooltip entity.tooltip
                    focus_mask True
                    background None
                # text "[entity.transform.pos] [entity.transform.zoom]" at _entity_transform(entity)
    
    # Lighting.
    if persistent.lighting_enabled:
        add scene_lighting_layer:
            blend "multiply"
    
    # UI elements.
    for ui_entity in scene.ui.values():
        imagebutton at updater_transform(ui_entity):
            idle ui_entity.image
            background None

    text "[scene.msg]":
        size 64
        color "#ffffff"

    # Highlight hovered entity.
    $ hover_entity = scene.hovering or hover_entity
    showif scene.hovering is not None:
        if hover_entity is not None:
            add hover_entity.image at [hover_entity.transform, scene_hovered]

    add scene_debug_layer

    # Cursor.
    fixed at updater_transform(scene.cursor):
        if scene.hovering == None:
            add Solid("#ff69b4") xsize 16 ysize 16