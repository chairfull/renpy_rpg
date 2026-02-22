def bracket_label(text, color="#ff3b3b", bracket_color="#ffffff"):
    """White square brackets w colored text inside."""
    return "{color=%s}[{/color}{color=%s}%s{/color}{color=%s}]{/color}" % (
        bracket_color, color, text, bracket_color
    )