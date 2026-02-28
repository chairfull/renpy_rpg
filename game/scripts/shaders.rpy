init python:

    # Horizontal pass
    renpy.register_shader("mygame.blur_h", variables="""
        uniform sampler2D tex0;
        uniform vec2      res0;
        uniform float     u_blur_amount;
        attribute vec2    a_tex_coord;
        varying vec2      v_tex_coord;
    """,
    vertex_300="""
        v_tex_coord = a_tex_coord;
    """,
    fragment_300="""
        float px = u_blur_amount / res0.x;
        vec4 color = vec4(0.0);

        // 9-tap bilinear Gaussian, horizontal only
        // Each fractional offset blends two texels via GPU bilinear = effectively 17-tap coverage
        color += texture2D(tex0, v_tex_coord + vec2(-7.0 * px, 0.0)) * 0.0044;
        color += texture2D(tex0, v_tex_coord + vec2(-5.0 * px, 0.0)) * 0.0540;
        color += texture2D(tex0, v_tex_coord + vec2(-3.0 * px, 0.0)) * 0.2420;
        color += texture2D(tex0, v_tex_coord + vec2(-1.0 * px, 0.0)) * 0.3990;
        color += texture2D(tex0, v_tex_coord)                        * 0.5000;
        color += texture2D(tex0, v_tex_coord + vec2( 1.0 * px, 0.0)) * 0.3990;
        color += texture2D(tex0, v_tex_coord + vec2( 3.0 * px, 0.0)) * 0.2420;
        color += texture2D(tex0, v_tex_coord + vec2( 5.0 * px, 0.0)) * 0.0540;
        color += texture2D(tex0, v_tex_coord + vec2( 7.0 * px, 0.0)) * 0.0044;

        gl_FragColor = color / 1.8988;
    """)

    # Vertical pass
    renpy.register_shader("mygame.blur_v", variables="""
        uniform sampler2D tex0;
        uniform vec2      res0;
        uniform float     u_blur_amount;
        attribute vec2    a_tex_coord;
        varying vec2      v_tex_coord;
    """,
    vertex_300="""
        v_tex_coord = a_tex_coord;
    """,
    fragment_300="""
        float px = u_blur_amount / res0.y;
        vec4 color = vec4(0.0);

        color += texture2D(tex0, v_tex_coord + vec2(0.0, -7.0 * px)) * 0.0044;
        color += texture2D(tex0, v_tex_coord + vec2(0.0, -5.0 * px)) * 0.0540;
        color += texture2D(tex0, v_tex_coord + vec2(0.0, -3.0 * px)) * 0.2420;
        color += texture2D(tex0, v_tex_coord + vec2(0.0, -1.0 * px)) * 0.3990;
        color += texture2D(tex0, v_tex_coord)                        * 0.5000;
        color += texture2D(tex0, v_tex_coord + vec2(0.0,  1.0 * px)) * 0.3990;
        color += texture2D(tex0, v_tex_coord + vec2(0.0,  3.0 * px)) * 0.2420;
        color += texture2D(tex0, v_tex_coord + vec2(0.0,  5.0 * px)) * 0.0540;
        color += texture2D(tex0, v_tex_coord + vec2(0.0,  7.0 * px)) * 0.0044;

        gl_FragColor = color / 1.8988;
    """)