init python:
    renpy.register_shader(
        "double_helix",
        variables="""
            uniform vec4 u_tint;
            uniform float u_thickness;
            uniform float u_amp;
            uniform float u_freq;
        """,
        fragment_100="""
            float y = tex_coord.y * u_freq * 6.2831853;
            float sx = sin(y) * u_amp;
            float x1 = 0.5 + sx;
            float x2 = 0.5 - sx;
            float d1 = abs(tex_coord.x - x1);
            float d2 = abs(tex_coord.x - x2);
            float strand = max(smoothstep(u_thickness, 0.0, d1), smoothstep(u_thickness, 0.0, d2));

            float rung_phase = sin(y * 0.5);
            float rung = smoothstep(u_thickness * 0.6, 0.0, abs(tex_coord.x - 0.5)) * smoothstep(0.6, 0.9, abs(rung_phase));

            float glow = strand * 0.9 + rung * 0.6;
            vec4 col = u_tint * glow;
            col.a = glow;
            gl_FragColor = col * color;
        """,
        fragment_200="""
            float y = tex_coord.y * u_freq * 6.2831853;
            float sx = sin(y) * u_amp;
            float x1 = 0.5 + sx;
            float x2 = 0.5 - sx;
            float d1 = abs(tex_coord.x - x1);
            float d2 = abs(tex_coord.x - x2);
            float strand = max(smoothstep(u_thickness, 0.0, d1), smoothstep(u_thickness, 0.0, d2));

            float rung_phase = sin(y * 0.5);
            float rung = smoothstep(u_thickness * 0.6, 0.0, abs(tex_coord.x - 0.5)) * smoothstep(0.6, 0.9, abs(rung_phase));

            float glow = strand * 0.9 + rung * 0.6;
            vec4 col = u_tint * glow;
            col.a = glow;
            gl_FragColor = col * color;
        """
    )
