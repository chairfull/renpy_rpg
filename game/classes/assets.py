from renpy.exports import loadable

def find_image(*args):
    path = "/".join(args)
    for ext in (".png", ".webp", ".jpg", ".svg"):
        full_path = f"../game/images/{path}{ext}"
        if loadable(full_path):
            return full_path
    return None