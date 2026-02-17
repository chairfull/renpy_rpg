init 10 python:
    class Shop(Inventory):
        def __init__(self, id, name, buy_mult=1.2, sell_mult=0.6, owner_id=None, **kwargs):
            super(Shop, self).__init__(id, name, owner_id=owner_id or id, **kwargs)
            self.buy_mult, self.sell_mult = buy_mult, sell_mult
            
        def get_buy_price(self, i):
            return int(i.value * self.buy_mult)

        def get_sell_price(self, i):
            return int(i.value * self.sell_mult)

        def interact(self):
            renpy.show_screen("shop_screen", shop=self)