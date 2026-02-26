init python:
    def _lights_screen_pos(light, camera):
        lx, _, lz = light.position
        cx, _, cz = camera.position
        zoom = camera.zoom
        sx = (lx - cx) * zoom + config.screen_width  / 2
        sz = (lz - cz) * zoom + config.screen_height / 2
        return int(sx), int(sz)

    class LightingLayer(renpy.Displayable):
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
                for l in scene.lights
            ))

            if not hasattr(self, "_last_state") or self._last_state != state:

                # Black = darkness; lights will carve out and tint illuminated areas.
                overlay = renpy.display.pgrender.surface((width, height), True)
                overlay.fill((0, 0, 0, 255))

                for light in scene.lights:
                    surf = self._get_surface(light, camera.zoom)
                    r = int(light.radius * camera.zoom)
                    sx, sz = _lights_screen_pos(light, camera)
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

define lighting = LightingLayer()