# AUTOMATICALLY GENERATED LABELS - DO NOT EDIT
label LOC__home__bed:
    "I'm not tired right now."
    return

label LOC__home__mirror:
    "You look great today!"
    return

label CHAR__shopkeeper__talk:
    shopkeeper "Welcome! I'll have some items for you soon."
    return

label CHAR__mayor__talk:
    mayor "Welcome to our town, traveler!"
    mayor "I hope you find everything to your liking."
    $ mayor.mark_as_met()
    $ mayor.items.append(Item("Town Map", "A map of the local area."))
    return

