import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django_cryptography.fields import encrypt

from account.models.managers import BaseModelManager, CustomUserManager


class BaseModel(models.Model):
    uuid = models.UUIDField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = BaseModelManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, hard_delete: bool = False, *args, **kwargs):
        if hard_delete:
            return super().delete(*args, **kwargs)
        else:
            self.deleted_at = timezone.now()
            self.save()


class CustomUser(AbstractUser, BaseModel):
    username = models.CharField(_("Username"), max_length=150, blank=True)
    email = models.EmailField(_('Email address'), unique=True)
    phone_number = models.CharField(_("Phone number"), max_length=11, blank=True)

    first_name = models.CharField(_("First name"), max_length=150)
    last_name = models.CharField(_("Last name"), max_length=150)

    verified_email = models.BooleanField(_('Verified email'), default=False)
    verified_phone = models.BooleanField(_('Verified phone number'), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Organization(BaseModel):
    uuid = models.UUIDField(default=uuid.uuid4)
    name = models.CharField(_('Name'), max_length=256)
    owner = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='organizations')
    balance = models.BigIntegerField(_('Balance'), default=0)

    def __str__(self):
        return self.name

    @property
    def members(self):
        return CustomUser.objects.filter(team=self)


class Otp(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = encrypt(models.CharField(_('token'), max_length=8))
    expiration_date = models.DateTimeField(_('Expiration date'))

    @classmethod
    def generate(cls, user: CustomUser, ttl: int = 10) -> str:
        cls.objects.filter(user=user).delete()
        token = get_random_string(length=8, allowed_chars="0123456789")
        expiration_date = timezone.now() + timedelta(minutes=ttl)
        cls.objects.create(
            user=user,
            token=token,
            expiration_date=expiration_date
        )
        return token

    @classmethod
    def validate(cls, user: CustomUser, token: str):
        return cls.objects.filter(user=user, token=token, expire_date__gt=timezone.now()).exists()


class OrganizationInvite(BaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    email = models.EmailField(_('Email address'))
    status = models.CharField(_('status'), max_length=16, choices=STATUS_CHOICES, default='pending')


class Payment(BaseModel):
    STATUS_CHOICES = [
        ('canceled', 'Canceled'),
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)
    amount = models.BigIntegerField(_('Amount'), )
    status = models.CharField(_('Status'), max_length=16, choices=STATUS_CHOICES, default='pending')
    authority_data = models.JSONField(_('Authority data'), blank=True, default=dict)
