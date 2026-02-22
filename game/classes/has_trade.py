from .has_items import HasItems

class HasTrade(HasItems):
    """Mixin for shopkeeps. Also used for pickpocketing."""
    def __init__(self, buy_mult=1.2, sell_mult=0.6, **kwargs):
        HasItems.__init__(**kwargs)
        self.buy_filters = [] # ItemFilter
        self.sell_filters = [] # ItemFilter
        self.buy_mult = buy_mult
        self.sell_mult = sell_mult
        
    def get_buy_price(self, item):
        return int(item.cost * self.buy_mult)
    
    def get_sell_price(self, item):
        return int(item.cost * self.sell_mult)