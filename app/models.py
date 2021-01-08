import uuid
from django.db import models
from django.db.models.signals import post_delete
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from phonenumber_field.modelfields import PhoneNumberField


class Wallet(models.Model):
    address = models.CharField(
        max_length=42,
        unique=True,
        validators=[RegexValidator(regex="^(tb1|[2nm]|bcrt)[a-zA-HJ-NP-Z0-9]{25,42}$")],
    )
    balance = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000000000)],
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
    wallet = models.OneToOneField(Wallet, on_delete=models.CASCADE)

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
    description = models.CharField(max_length=120, blank=True, null=True)
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(100000000)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
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


class Invoice(models.Model):
    bolt11_invoice = models.CharField(
        max_length=500,
        null=True,
        validators=[RegexValidator(regex="^lntb(\d{1,12})(\w{200,550})$")],
    )
    created_at = models.DateTimeField(auto_now_add=True)
    value = models.PositiveIntegerField(
        validators=[MinValueValidator(100), MaxValueValidator(100000000)]
    )
    payer = models.ForeignKey(
        User, related_name="payer_invoices", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]


@receiver(post_delete, sender=User)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.wallet:
        instance.wallet.delete()
