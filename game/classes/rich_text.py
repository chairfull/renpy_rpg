"""
rich_text.py — BBCode+Markdown → Ren'Py formatter and rich-text runtime.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Syntax reference  (for convert())
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  |text|                 {b}text{/b}           bold
  _text_                 {i}text{/i}           italic

  [tag]content]          {tag}content{/tag}
  [t1;t2]content]        nested, closes reversed
  []content]             strip formatting
  [color outline]text]   {color=...}{outlinecolor=...}
  [_ outline]text]       outline only
  [jitter]text]          {shader=jitter}text{/shader}  (unknown → shader)
  [lb]                   [[   (Ren'Py literal [)   ← self-closing, no ]
  [rb]                   ]    (literal ])           ← self-closing, no ]

  "text"                 "text"  (curly smart quotes)

  {expr}                 [to_rich_text(expr)]
  {expr|key=val n=3}     [to_rich_text(expr, key="val", n=3)]
  {!expr}                [expr]   raw — skips to_rich_text entirely

  $name.                 [to_rich_text(name)].   property shorthand

  Size tags:  [24]  [*0.5]  [+4]  [-2]
"""

import re
from typing import Any
from .has_rich_text import HasRichText

# ─────────────────────────────────────────────────────────────────────────────
# Color dictionary
# ─────────────────────────────────────────────────────────────────────────────

COLOR_MAP: dict[str, str] = {
    "black":       "#000000", "white":       "#ffffff",
    "red":         "#ff0000", "green":       "#008000",
    "blue":        "#0000ff", "yellow":      "#ffff00",
    "cyan":        "#00ffff", "magenta":     "#ff00ff",
    "orange":      "#ffa500", "purple":      "#800080",
    "pink":        "#ffc0cb", "brown":       "#a52a2a",
    "gray":        "#808080", "grey":        "#808080",
    "lime":        "#00ff00", "navy":        "#000080",
    "teal":        "#008080", "maroon":      "#800000",
    "olive":       "#808000", "silver":      "#c0c0c0",
    "gold":        "#ffd700", "coral":       "#ff7f50",
    "salmon":      "#fa8072", "violet":      "#ee82ee",
    "indigo":      "#4b0082", "turquoise":   "#40e0d0",
    "crimson":     "#dc143c", "khaki":       "#f0e68c",
    "lavender":    "#e6e6fa", "beige":       "#f5f5dc",
    "ivory":       "#fffff0", "mint":        "#98ff98",
    "rose":        "#ff007f", "peach":       "#ffcba4",
    "amber":       "#ffbf00", "emerald":     "#50c878",
    "sapphire":    "#0f52ba", "ruby":        "#9b111e",
    "tan":         "#d2b48c", "chocolate":   "#d2691e",
    "tomato":      "#ff6347", "aqua":        "#00ffff",
    "fuchsia":     "#ff00ff", "orchid":      "#da70d6",
    "plum":        "#dda0dd", "sienna":      "#a0522d",
    "skyblue":     "#87ceeb", "steelblue":   "#4682b4",
    "hotpink":     "#ff69b4", "deeppink":    "#ff1493",
    "limegreen":   "#32cd32", "darkgreen":   "#006400",
    "darkblue":    "#00008b", "darkred":     "#8b0000",
    "darkorange":  "#ff8c00", "darkviolet":  "#9400d3",
    "lightgray":   "#d3d3d3", "lightgrey":   "#d3d3d3",
    "lightblue":   "#add8e6", "lightgreen":  "#90ee90",
    "lightyellow": "#ffffe0", "lightpink":   "#ffb6c1",
    "lightcoral":  "#f08080", "wheat":       "#f5deb3",
}

_HEX_RE      = re.compile(r"^#[0-9a-fA-F]{3,8}$")
_SIZE_RE     = re.compile(r"^([*+\-])(\d+(?:\.\d+)?|\.\d+)$|^(\d+)$")
_NUMBER_RE   = re.compile(r"^[+\-]?(\d{1,3}(?:,\d{3})*|\d+)(\.\d+)?$")
_INT_RE      = re.compile(r"^-?\d+$")
_FLOAT_RE    = re.compile(r"^-?\d*\.\d+$")
_SIMPLE_TAGS = {"b","i","u","s","plain","art","cps","nw","p","w","fast","slow"}

_OPEN_QUOTE  = "\u201c"
_CLOSE_QUOTE = "\u201d"

# Auto-color applied to int/float values. Change to suit your palette.
NUMBER_COLOR = "#ffd700"


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_color(name: str) -> str:
    return COLOR_MAP.get(name.lower(), name)


def _resolve_single_tag(tag: str) -> list[tuple[str, str]]:
    """Return [(open, close), ...] for one tag token."""
    t = tag.strip()
    if not t or t == "_":
        return []
    tl = t.lower()

    # Space-separated color pair: "fg bg" or "_ bg"
    parts = t.split()
    if len(parts) == 2:
        fg, bg = parts
        result: list[tuple[str, str]] = []
        if fg != "_":
            result.append((f"{{color={_resolve_color(fg)}}}", "{/color}"))
        if bg != "_":
            result.append((f"{{outlinecolor={_resolve_color(bg)}}}", "{/outlinecolor}"))
        return result

    if tl in COLOR_MAP: return [(f"{{color={COLOR_MAP[tl]}}}", "{/color}")]
    if _HEX_RE.match(t): return [(f"{{color={t}}}", "{/color}")]
    if tl in _SIMPLE_TAGS: return [(f"{{{tl}}}", f"{{/{tl}}}")]
    if _SIZE_RE.match(t): return [(f"{{size={t}}}", "{/size}")]

    kv = re.fullmatch(r"(\w+)=(\S+)", t)
    if kv:
        return [(f"{{{t}}}", f"{{/{kv.group(1)}}}")]

    return [(f"{{shader={t}}}", "{/shader}")]


def _resolve_tag_header(header: str) -> tuple[list[str], list[str]]:
    opens, closes = [], []
    for part in header.split(";"):
        for o, c in _resolve_single_tag(part.strip()):
            opens.append(o)
            closes.append(c)
    closes.reverse()
    return opens, closes


def _find_content_end(text: str, start: int) -> int:
    """Find the ] closing the current BBCode content block, skipping nested blocks."""
    i, n = start, len(text)
    while i < n:
        ch = text[i]
        if ch == "[":
            j = text.find("]", i + 1)
            if j == -1: return -1
            i = j + 1
            k = _find_content_end(text, i)
            if k == -1: return -1
            i = k + 1
        elif ch == "]":
            return i
        else:
            i += 1
    return -1


def _parse_context(ctx_str: str) -> dict[str, str]:
    """
    Parse 'key=val key2=val2' context string into a dict of emittable strings.
    Integers and floats stay numeric; everything else becomes a quoted string.
    'as' is silently remapped to 'form' to avoid Python keyword collision.
    """
    result: dict[str, str] = {}
    for part in ctx_str.split():
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        k = k.strip()
        v = v.strip()
        if k == "as":
            k = "form"
        if _INT_RE.match(v):
            result[k] = v
        elif _FLOAT_RE.match(v):
            result[k] = v
        else:
            result[k] = f'"{v}"'
    return result


def _kwargs_str(kwargs: dict[str, str]) -> str:
    return ", ".join(f"{k}={v}" for k, v in kwargs.items())


# ─────────────────────────────────────────────────────────────────────────────
# convert()  — build-time BBCode+Markdown → Ren'Py tags
# ─────────────────────────────────────────────────────────────────────────────

def convert(text: str, _qopen: list | None = None) -> str:
    """
    Convert custom BBCode+Markdown syntax to Ren'Py formatting tags.

    Intended for build-time pre-processing of dialogue scripts.
    """
    if _qopen is None:
        _qopen = [True]   # True = next " is an opening quote

    result: list[str] = []
    i, n = 0, len(text)

    while i < n:
        ch = text[i]

        # ── BBCode block: [tag(s)]content]  ───────────────────────────────
        if ch == "[":
            header_end = text.find("]", i + 1)
            if header_end == -1:
                result.append(ch); i += 1; continue

            tag_str = text[i + 1 : header_end]

            # Self-closing tags — no content bracket consumed
            if tag_str == "lb":
                result.append("[[")          # Ren'Py literal [
                i = header_end + 1
                continue
            if tag_str == "rb":
                result.append("]")           # literal ]
                i = header_end + 1
                continue

            content_start = header_end + 1
            content_end   = _find_content_end(text, content_start)
            if content_end == -1:
                result.append(ch); i += 1; continue

            inner = convert(text[content_start : content_end], _qopen)

            if not tag_str:
                result.append(inner)
            else:
                opens, closes = _resolve_tag_header(tag_str)
                result.append("".join(opens))
                result.append(inner)
                result.append("".join(closes))

            i = content_end + 1

        # ── {expr}  {expr|ctx}  {!expr}  →  [...] ─────────────────────────
        elif ch == "{":
            j = text.find("}", i + 1)
            if j == -1:
                result.append(ch); i += 1; continue

            inner = text[i + 1 : j]

            # {!expr} — raw, no to_rich_text wrapping
            if inner.startswith("!"):
                result.append(f"[{inner[1:].strip()}]")
            else:
                # Split expr from context args on first |
                if "|" in inner:
                    expr, ctx_raw = inner.split("|", 1)
                    expr    = expr.strip()
                    kwargs  = _parse_context(ctx_raw.strip())
                    kw_str  = _kwargs_str(kwargs)
                    result.append(f"[to_rich_text({expr}, {kw_str})]")
                else:
                    result.append(f"[to_rich_text({inner.strip()})]")

            i = j + 1

        # ── Smart quotes: "  →  " / " ──────────────────────────────────────
        elif ch == '"':
            result.append(_OPEN_QUOTE if _qopen[0] else _CLOSE_QUOTE)
            _qopen[0] = not _qopen[0]
            i += 1

        # ── |bold| ─────────────────────────────────────────────────────────
        elif ch == "|":
            j = text.find("|", i + 1)
            if j == -1:
                result.append(ch); i += 1
            else:
                inner = convert(text[i + 1 : j], _qopen)
                result.append(f"{{b}}{inner}{{/b}}")
                i = j + 1

        # ── _italic_ ───────────────────────────────────────────────────────
        elif ch == "_":
            j = text.find("_", i + 1)
            if j == -1:
                result.append(ch); i += 1
            else:
                inner = convert(text[i + 1 : j], _qopen)
                result.append(f"{{i}}{inner}{{/i}}")
                i = j + 1

        # ── $name. → [to_rich_text(name)]. ────────────────────────────────
        elif ch == "$":
            j = text.find(".", i + 1)
            if j == -1:
                result.append(ch); i += 1
            else:
                result.append(f"[to_rich_text({text[i+1:j]})].")
                i = j + 1

        else:
            result.append(ch)
            i += 1

    return "".join(result)

def _fmt_number(v: int | float) -> str:
    if isinstance(v, int):
        return f"{v:,}"
    s = f"{v:,.10f}".rstrip("0").rstrip(".")
    return s

def _color_wrap(text: str, color: str) -> str:
    return f"{{color={color}}}{text}{{/color}}"

def to_rich_text(obj: Any, **kwargs) -> str:
    """
    Convert any value to a Ren'Py-ready rich text string.

    Called at runtime from every [to_rich_text(expr)] produced by convert().
    Context kwargs come from the {expr|key=val} syntax in source text.

    Resolution order:
      HasRichText                      → to_rich_string(**kwargs)
      list / tuple                     → Oxford-comma join, each item dispatched
      None                             → ""
      int / float                      → comma-formatted, auto-colored
      str that looks numeric           → auto-colored
      str                              → as-is
      anything else                    → str(obj)
    """

    # ── HasRichText ──────────────────────────────────────────────────────
    if isinstance(obj, HasRichText):
        return obj.to_rich_string(**kwargs)

    # ── list / tuple ───────────────────────────────────────────────────────
    if isinstance(obj, (list, tuple)):
        parts = [to_rich_text(item, **kwargs) for item in obj]
        if len(parts) == 0: return ""
        if len(parts) == 1: return parts[0]
        if len(parts) == 2: return f"{parts[0]} and {parts[1]}"
        return ", ".join(parts[:-1]) + f", and {parts[-1]}"

    # ── None ───────────────────────────────────────────────────────────────
    if obj is None:
        return ""

    # ── Numbers ────────────────────────────────────────────────────────────
    if isinstance(obj, (int, float)):
        return _color_wrap(_fmt_number(obj), NUMBER_COLOR)

    # ── Strings ────────────────────────────────────────────────────────────
    if isinstance(obj, str):
        if _NUMBER_RE.match(obj.strip()):
            return _color_wrap(obj, NUMBER_COLOR)
        return obj

    return str(obj)