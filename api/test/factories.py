import factory
import phonenumbers
from faker.providers.phone_number.en_US import Provider
from faker import Faker

fake = Faker()


class CustomPhoneProvider(Provider):
    def phone_number(self):
        while True:
            phone_number = self.numerify(self.random_element(self.formats))
            parsed_number = phonenumbers.parse(phone_number, "US")
            if phonenumbers.is_valid_number(parsed_number):
                return phonenumbers.format_number(
                    parsed_number, phonenumbers.PhoneNumberFormat.E164
                )


fake.add_provider(CustomPhoneProvider)


class WalletFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Wallet"

    @classmethod
    def generate_address(self):
        return fake.pystr_format(
            string_format="tb1?#?#?#?##??##???#?#?#?#??#?#?#?#?#??##?",
            letters="abcdefghijklmnopqrstuvwxyz",
        )

    address = factory.Faker(
        "pystr_format",
        string_format="tb1?#?#?#?##??##???#?#?#?#??#?#?#?#?#??##?",
        letters="abcdefghijklmnopqrstuvwxyz",
    )
    balance = factory.Faker("pyint", min_value=1, max_value=10000000)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.User"
        django_get_or_create = ("phone_number",)

    id = factory.Faker("uuid4")
    phone_number = factory.LazyAttribute(lambda _: fake.phone_number())
    wallet = factory.SubFactory(WalletFactory)
