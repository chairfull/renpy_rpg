import renpy
from . import engine
from .has_tags import HasTags

class Craft(HasTags):
    def __init__(self, _id, name, inputs, output, req_skill=None, tags=None):
        HasTags.__init__(self, tags)
        self.id = _id
        self.name = name
        self.inputs = inputs
        self.output = output
        self.req_skill = req_skill
        engine.all_crafts[_id] = self

    def can_craft(self, items):
        for item, count in self.inputs.items():
            if not items.has_item(item, count):
                return False, f"Missing {item.id}"

        if self.req_skill:
            for skill, level in self.req_skill.items():
                if engine.player.get_trait(skill) < level:
                    return False, f"Need {skill} {level}"
                
        return True, "OK"

    def craft(self, items):
        can, msg = self.can_craft(items)
        if not can:
            renpy.notify(msg)
            return False
        
        # Consume inputs
        for item, count in self.craft.inputs.items():
            items.remove_item(item, count=count)
        
        # Grant outputs
        for item, count in self.craft.output.items():
            items.add_item(item, count=count, force=True)
        
        renpy.notify(f"Crafted {self.name}")
        engine.ITEM_CRAFTED.emit(craft=self)
        return True