import factory
from faker import Faker

fake = Faker()


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
    balance = factory.Faker("pydecimal", left_digits=1, right_digits=8, positive=True)
