label CHAR__mayor__history:
    mayor "Our town was founded 200 years ago by a group of merchants."
    mayor "We've prospered ever since thanks to our position on the trade route."
    return

label CHAR__mayor__compliment:
    mayor "Why thank you! A leader must always look his best."
    $ pc.gold += 50
    "The Mayor gives you 50 gold for the compliment."
    return

label SCENE__intro__mercenary:
    "You arrive at the market square, your sword heavy at your side."
    "The air is thick with the smell of spices and the sound of bartering."
    "Your journey as a mercenary begins here."
    jump world_loop

label SCENE__intro__scholar:
    "You wake up in your familiar study, surrounded by stacks of ancient parchment."
    "The sunlight filters through the window, illuminating dust motes in the air."
    "Today is the day you begin your grand research into the town's history."
    jump world_loop
