init python:
    # Locations
    home_location = Location(id="home", name="Your Home", description="A cozy, albeit small, house.")
    square_location = Location(id="square", name="Town Square", description="The bustling heart of the town.")
    shop_location = Location(id="shop", name="General Store", description="A shop filled with various goods.")

    # Connections
    home_location.add_connection("square", "Leave your house")
    square_location.add_connection("home", "Go home")
    square_location.add_connection("shop", "Visit the shop")
    shop_location.add_connection("square", "Exit to square")

    # Add to world
    rpg_world.add_location(home_location)
    rpg_world.add_location(square_location)
    rpg_world.add_location(shop_location)

    # Initialize Shop
    general_store = Shop(name="AI General Store", description="The best place for supply.")
    shop_location.add_entity(general_store)
    
    # Populate Shop Inventory from ItemManager
    # (Checking if items exist in registry)
    for i_id in ["sword", "apple", "potion"]:
        itm = item_manager.get(i_id)
        if itm:
            # Add a few of each
            for i in range(3):
                general_store.add_item(item_manager.get(i_id))

    # Characters (already registered via MarkdownParser, but we link them here for interaction if needed)
    # The MarkdownParser handles character registration and location association automatically.
    
    # Custom interaction for shopkeeper (redirect to shop screen)
    def shopkeeper_interaction():
        renpy.say(None, "Welcome to my shop! Take a look at my wares.")
        general_store.interact()
    
    # Find the shopkeeper character and override interaction
    # (Assuming name "Shopkeeper" from shopkeeper.md)
    shopkeeper_npc = rpg_world.characters.get("Shopkeeper")
    if shopkeeper_npc:
        shopkeeper_npc.label = None # Disable label jump
        shopkeeper_npc.interact = shopkeeper_interaction

    # Entities
    # The closet is handled via container MD and automatically added to home.
