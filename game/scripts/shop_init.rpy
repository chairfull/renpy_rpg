init 10 python:
    # Initialize Shop manually for now since it has custom logic (buy/sell multipliers)
    # This ensures it exists even without locations.rpy
    
    shop_loc = rpg_world.locations.get("shop")
    if shop_loc:
        general_store = Shop(id="general_store", name="AI General Store", description="The best place for supply.")
        
        # Add to shop location entities if not already there
        # (Though with new system, we might want to register it as an entity in YAML eventually)
        # For now, we manually append it to the entity list for the engine to find interactions
        
        # We need to wrap it in a pseudo-entity structure if the engine expects raw dicts, 
        # BUT the engine's setup() iterates `location.entities` which are dicts from YAML.
        # The `shop.md` has `entities: []`.
        
        # ACTUALLY: The topdown engine expects `TopDownEntity` objects.
        # The `instantiate_all` loads YAML dicts into `location.entities`.
        # If we want a Python object `Shop` to be interactive, we should add it to the entity list via a special handler or just let the YAML define a "Shopkeeper" entity that calls `general_store.interact()`.

        # Let's populate the shop inventory
        for i_id in ["sword", "apple", "potion"]:
            itm = item_manager.get(i_id)
            if itm:
                for i in range(3):
                    general_store.add_item(item_manager.get(i_id))

    # Define the interaction function for the shopkeeper
    def shopkeeper_interaction():
        renpy.say(None, "Welcome to my shop! Take a look at my wares.")
        # Ensure general_store is accessible
        if 'general_store' in globals():
            general_store.interact()
        else:
            renpy.notify("Shop is closed (Error: general_store not found)")

    # Hook this up to the Shopkeeper character
    # We need to ensure this runs AFTER characters are loaded
    shopkeeper_npc = rpg_world.characters.get("Shopkeeper")
    if shopkeeper_npc:
        shopkeeper_npc.interact = shopkeeper_interaction
