import uuid
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from decimal import Decimal


class Wallet(models.Model):
    address = models.CharField(
        max_length=42,
        unique=True,
        validators=[RegexValidator(regex="^(tb1|[2nm]|bcrt)[a-zA-HJ-NP-Z0-9]{25,42}$")],
    )
    balance = models.DecimalField(
        max_digits=10, decimal_places=8, default=Decimal("0.0")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]


class User(AbstractUser):
    first_name = None
    last_name = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = PhoneNumberField(unique=True)
    wallet = models.OneToOneField(Wallet, null=True, on_delete=models.CASCADE)

    EMAIL_FIELD = None
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.username = str(self.phone_number)
        return super(User, self).save(*args, **kwargs)


class Payment(models.Model):
    class Status(models.IntegerChoices):
        OPEN = 0
        SETTLED = 1
        CANCELED = 2

    invoice = models.CharField(
        max_length=500,
        null=True,
        validators=[RegexValidator(regex="^lntb(\d{1,12})(\w{200,550})$")],
    )
    description = models.CharField(max_length=120, blank=True, null=True)
    value = models.IntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(100000000)]
    )  # Satoshis
    status = models.PositiveSmallIntegerField(
        choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(blank=True, null=True)
    payer = models.ForeignKey(
        User, related_name="payer_payments", on_delete=models.CASCADE
    )
    payee = models.ForeignKey(
        User, related_name="payee_payments", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Payment #{self.id} from {self.payer} to {self.payee}"

    # TODO: When the status change to settle update the settle_at, or remove that field
