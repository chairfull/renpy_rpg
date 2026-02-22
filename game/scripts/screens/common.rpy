init -3000 python:
    from classes import util_color
    def text_outline(color, outline_factor=0.45, shadow_factor=0.2, shadow_alpha=80):
        """Returns colored text w outline of same color and a faint shadow."""
        outline = util_color.rgb_to_hex(util_color.tint(color, outline_factor))
        shadow = util_color.rgb_to_hex(util_color.tint(color, shadow_factor), shadow_alpha)
        return [(2, outline, 0, 0), (2, shadow, 0, 2)]

    def mm_button_style(color, hover_color=None):
        if hover_color is None:
            hover_color = "#ffffff"
        s = Style(style.mm_button_text)
        s.color = color
        s.hover_color = hover_color
        s.outlines = text_outline(color)
        return s

# This is a placeholder cell screen. Replace with actual content based on cell_data.
screen grid_page_cell(cell_data):
    frame:
        background "#1a1a25"
        xsize 120
        ysize 120
        align (0.5, 0.5)
        if cell_data:
            text "Cell" color "#fff" xalign 0.5 yalign 0.5
        else:
            text "" xalign 0.5 yalign 0.5

# Displays a grid of cells, with pagination if there are more cells than fit on one page.
screen grid_page(wide, high, cells):
    default current_page = 0
    $ cells_per_page = wide * high
    $ total_pages = (len(cells) + cells_per_page - 1) // cells_per_page

    frame:
        # background "#000a"
        padding (20, 20)
        vbox:
            spacing 10
            for y in range(high):
                hbox:
                    spacing 10
                    for x in range(wide):
                        $ cell_index = y * wide + x
                        if cell_index < len(cells):
                            use grid_page_cell(cells[cell_index])
                        else:
                            use grid_page_cell(None)  # Empty cell for padding

            hbox:
                spacing 10
                xalign 0.5
                for page in range(total_pages):
                    # draw page icons
                    if page == current_page:
                        text "●" size 20 color "#ffd700"
                    else:
                        textbutton "○" text_size 20 text_color "#999" action SetScreenVariable("current_page", page)

# Commonly applied to buttons to create a standard effect.
transform button_hover_effect:
    on hover:
        block:
            ease 0.5 matrixcolor BrightnessMatrix(0.3) * SaturationMatrix(1.5) * HueMatrix(180)
        block:
            ease 1.0 matrixcolor BrightnessMatrix(0.1) * SaturationMatrix(1.0) * HueMatrix(180)
            ease 0.25 matrixcolor BrightnessMatrix(0.3) * SaturationMatrix(1.5) * HueMatrix(180)
            repeat
    on idle:
        ease 0.125 matrixcolor BrightnessMatrix(0.0) * SaturationMatrix(1.0) * HueMatrix(0)

transform text_hover_anim:
    subpixel True
    on hover:
        block:
            ease 0.5 zoom 1.2 rotate -10
        block:
            easein_back 1.0 zoom 0.9 rotate 5
            easein_back 0.25 zoom 1.2 rotate -10
            repeat
    on idle:
        easein_back 0.25 zoom 1.0 rotate 0