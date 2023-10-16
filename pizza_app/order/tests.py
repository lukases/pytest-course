import factory
import pytest
from freezegun import freeze_time

from order.factories import PizzaFactory, SizeFactory, ToppingFactory
from order.models import Size
from order.services import OrderPizzaService


@pytest.mark.django_db
class TestOrderPizzaService:
    @pytest.fixture
    def pepperoni_pizza(self):
        pizza = PizzaFactory(name="Pepperoni", description="Pepperoni pizza")
        toppings = ToppingFactory.create_batch(2, description=factory.Iterator(["Cheese", "Pepperoni"]), price=factory.Iterator([5.00, 7.00]))
        pizza.toppings.set(toppings)
        return pizza
    
    @pytest.fixture
    def chicken_pizza(self):
        pizza = PizzaFactory(name="Chicken", description="Chicken pizza")
        toppings = ToppingFactory.create_batch(3, description=factory.Iterator(["Chicken", "Cheese", "Corn"]), price=factory.Iterator([6.00, 5.00, 2.00]))
        pizza.toppings.set(toppings)
        return pizza
    
    @pytest.fixture
    def sizes(self):
        return SizeFactory.create_batch(3, description=factory.Iterator(["Small", "Medium", "Large"]), price=factory.Iterator([15.00, 21.50, 32.50]))
    
    @pytest.mark.parametrize("pizza, price", [("pepperoni_pizza", 12.00), ("chicken_pizza", 13.00)])
    def test_get_pizza_price(self, pepperoni_pizza, chicken_pizza, pizza, price):
        assert eval(pizza).total_price == price

    @pytest.mark.usefixtures("sizes")
    def test_order_pizza_with_no_extra_toppings(self, pepperoni_pizza):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")

        # Calculating results
        service = OrderPizzaService(address="test")
        order = service.order_pizza(pizza_orders=[(pepperoni_pizza, medium_size, None)], notes="test")

        # Assertion
        assert order.pizzas.count() == 1
        pizza_order = order.pizzas.first()
        assert pizza_order.pizza == pepperoni_pizza
        assert pizza_order.size == medium_size
        assert pizza_order.extra_toppings.count() == 0
        assert pizza_order.total_price == 33.50
        assert order.price == 33.50

    @pytest.mark.usefixtures("sizes")
    def test_order_pizza_with_extra_toppings(self, pepperoni_pizza):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")
        extra_toppings = ToppingFactory.create_batch(2, description=factory.Iterator(["Mushrooms", "Onions"]), price=factory.Iterator([4.00, 2.00]))

        # Calculating results
        service = OrderPizzaService(address="test")
        order = service.order_pizza(pizza_orders=[(pepperoni_pizza, medium_size, extra_toppings)], notes="test")

        # Assertion
        assert order.pizzas.count() == 1
        pizza_order = order.pizzas.first()
        assert pizza_order.pizza == pepperoni_pizza
        assert pizza_order.size == medium_size
        assert pizza_order.extra_toppings.count() == 2
        assert pizza_order.total_price == 39.50
        assert order.price == 39.50

    @pytest.mark.usefixtures("sizes")
    def test_order_two_pizzas(self, pepperoni_pizza, chicken_pizza):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")
        large_size = Size.objects.get(description="Large")
        extra_topping = ToppingFactory(description="Bacon", price=3.50)

        # Calculating results
        service = OrderPizzaService(address="test")
        order = service.order_pizza(pizza_orders=[
                (pepperoni_pizza, medium_size, None), 
                (chicken_pizza, large_size, [extra_topping])
            ],
            notes="test",
        )

        # Assertion
        assert order.pizzas.count() == 2
        pizza_order_1 = order.pizzas.first()
        assert pizza_order_1.pizza == pepperoni_pizza
        assert pizza_order_1.size == medium_size
        assert pizza_order_1.extra_toppings.count() == 0
        assert pizza_order_1.total_price == 33.50

        pizza_order_2 = order.pizzas.last()
        assert pizza_order_2.pizza == chicken_pizza
        assert pizza_order_2.size == large_size
        assert pizza_order_2.extra_toppings.count() == 1
        assert pizza_order_2.total_price == 49.00

        assert order.price == 82.50

    # Rodar o coverage (pytest --cov=. --cov-report=html)

    def test_no_pizza_order_provided(self):
        # Preparation phase
        service = OrderPizzaService(address="test")

        # Assertion
        with pytest.raises(ValueError):
            service.order_pizza(pizza_orders=[])

    @pytest.mark.usefixtures("sizes")
    def test_no_pizza_provided(self):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")
        service = OrderPizzaService(address="test")

        # Assertion
        with pytest.raises(ValueError):
            service.order_pizza(pizza_orders=[(None, medium_size, None)])

    def test_no_size_provided(self, chicken_pizza):
        # Preparation phase
        service = OrderPizzaService(address="test")

        # Assertion
        with pytest.raises(ValueError):
            service.order_pizza(pizza_orders=[(chicken_pizza, None, None)])

    @pytest.mark.usefixtures("sizes")
    @freeze_time("2023-10-19 19:29:00")
    def test_order_in_time(self, pepperoni_pizza):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")

        # Calculating results
        with freeze_time("2023-10-19 19:00:00"):
            service = OrderPizzaService(address="test")
            order = service.order_pizza(pizza_orders=[(pepperoni_pizza, medium_size, None)])

        # Assertion
        assert order.in_time

    @pytest.mark.usefixtures("sizes")
    @freeze_time("2023-10-19 19:31:00")
    def test_order_out_of_time(self, pepperoni_pizza):
        # Preparation phase
        medium_size = Size.objects.get(description="Medium")

        # Calculating results
        with freeze_time("2023-10-19 19:00:00"):
            service = OrderPizzaService(address="test")
            order = service.order_pizza(pizza_orders=[(pepperoni_pizza, medium_size, None)])

        # Assertion
        assert not order.in_time
