import factory
import phonenumbers
import string
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
    balance = factory.Faker("pyint", min_value=50000, max_value=10000000)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.User"
        django_get_or_create = ("phone_number",)

    id = factory.Faker("uuid4")
    phone_number = factory.LazyAttribute(lambda _: fake.phone_number())
    wallet = factory.SubFactory(WalletFactory)


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Payment"

    value = factory.Faker("pyint", min_value=100, max_value=50000)
    description = factory.Faker("text", max_nb_chars=100)
    payer = factory.SubFactory(UserFactory)
    payee = factory.SubFactory(UserFactory)


class InvoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "app.Invoice"

    value = factory.Faker("pyint", min_value=100, max_value=50000)
    fee = factory.Faker("pyint", min_value=100, max_value=50000)
    payer = factory.SubFactory(UserFactory)
    description = factory.Faker("text", max_nb_chars=100)
    bolt11_invoice = factory.Sequence(
        lambda n: "lntb10n1p0lh85wpp5xrwns2zw25ukgezve4lgfq4qvxjapc3yxgj4swlzmrc4lh2zmr19"
        "sdqqcqzpgxqyz5vqsp5qecmn59nc5pxapcy2gsmwdx0kplqr99x5pj9pzv0wumlwppmy0ss9qyyssqg7"
        "8n363qf5jfr5dk2e3xadffff52cpjvcjsuumqrht6t7hyh73hyyncreaw3ynq9qp0t58hff2u29n8vaw"
        "w8zz2lk4u9cmq6k89eg6gpazqjly"
        + "".join(
            fake.random_elements(
                elements=(string.ascii_uppercase + string.digits), length=9, unique=True
            )
        ).lower()
    )
