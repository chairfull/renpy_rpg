init python:
    class Minigame:
        def __init__(self, name, label):
            self.name = name
            self.label = label

        def start(self):
            renpy.call(self.label)

    # Example minigame: A simple dice roll check
    def roll_dice_minigame(stat_name, difficulty):
        roll = random.randint(1, 20)
        try:
            stat_value = rpg_world.actor.get_stat_total(stat_name)
        except Exception:
            stat_value = getattr(rpg_world.actor.stats, stat_name)
        total = roll + (stat_value - 10) // 2
        
        renpy.say(None, f"Rolling for {stat_name}... You rolled a {roll} + { (stat_value - 10) // 2 } bonus.")
        
        if total >= difficulty:
            renpy.say(None, f"Success! ({total} >= {difficulty})")
            return True
        else:
            renpy.say(None, f"Failure... ({total} < {difficulty})")
            return False

# Label to trigger minigame from game
label test_minigame:
    "Let's test your strength!"
    $ result = roll_dice_minigame("strength", 12)
    if result:
        "You feel stronger already."
    else:
        "Maybe next time."
    jump world_loop

# The training dummy is now handled through the square.md data file.
