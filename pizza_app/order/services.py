from django.db import transaction
from order.models import Order, Pizza, Size, Topping
from typing import List, Optional, Tuple


class OrderPizzaService:
    def __init__(self, address: str = "") -> None:
        self.address = address

    @transaction.atomic
    def order_pizza(self, pizza_orders: List[Tuple[Pizza, Size, Optional[List[Topping]]]], notes: str = "") -> Order:
        if not pizza_orders:
            raise ValueError('No pizza order provided')
        
        order = Order.objects.create(notes=notes, address=self.address, status=0)

        for pizza_order in pizza_orders:
            if not pizza_order[0]:
                raise ValueError('No pizza provided')
            
            if not pizza_order[1]:
                raise ValueError('No size provided')

            p_order = order.pizzas.create(pizza=pizza_order[0], size=pizza_order[1])

            if pizza_order[2]:
                p_order.extra_toppings.set(pizza_order[2])
            
        order.save()

        return order
    
    def update_notes(self, order_id: int) -> Order:
        order = Order.objects.get(id=order_id)
        order.notes = self.address
        order.save()

        return order
