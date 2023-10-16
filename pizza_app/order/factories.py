import factory
from order.models import Order, Pizza, PizzaOrder, Size, Topping


class SizeFactory(factory.django.DjangoModelFactory):
    description = factory.Faker('name')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)

    class Meta:
        model = Size


class ToppingFactory(factory.django.DjangoModelFactory):
    description = factory.Faker('name')
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)

    class Meta:
        model = Topping


class PizzaFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    description = factory.Faker('text')

    class Meta:
        model = Pizza


class OrderFactory(factory.django.DjangoModelFactory):
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    notes = factory.Faker('text')
    address = factory.Faker('address')
    status = 0

    class Meta:
        model = Order


class PizzaOrderFactory(factory.django.DjangoModelFactory):
    pizza = factory.SubFactory(PizzaFactory)
    size = factory.SubFactory(SizeFactory)
    order = factory.SubFactory(OrderFactory)

    class Meta:
        model = PizzaOrder
