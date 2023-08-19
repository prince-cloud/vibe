import secrets
from typing import Dict
from rest_framework import serializers
from config.sms import send_sms
from .models import CustomUser
from django.db import transaction

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import validate_phonenumber
from django.utils import timezone


class UserAccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
        ]


class MyTokenObtainPairSerializer(TokenObtainPairSerializer, UserAccountSerializer):
    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        password = attrs.get("password")
        user_account_qs = CustomUser.objects.filter(phone_number=phone_number)
        if user_account_qs.exists():
            user_account: CustomUser = user_account_qs.first()
            if (not user_account.is_active) and user_account.check_password(password):
                self.error_messages["no_active_account"] = _(
                    "The account is inactive. Please verify account."
                )
        attrs = super().validate(attrs)
        self.instance = self.user
        attrs.update(UserAccountSerializer(instance=self.user).data)
        return attrs

    class Meta(UserAccountSerializer.Meta):
        read_only_fields = (
            "id",
            "first_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "is_online",
            "last_login",
            "last_name",
            "phone_number",
            "date_joined",
        )


class UserAccountSerializerWithToken(serializers.ModelSerializer):
    access = serializers.CharField(max_length=500, read_only=True)
    refresh = serializers.CharField(max_length=500, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "access",
            "refresh",
            "phone_number",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
        ]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "phone_number",
            "password",
        )

    def validate(self, attrs):
        phone_number = attrs["phone_number"]
        first_name = attrs["first_name"]
        last_name = attrs["last_name"]
        if not(first_name or last_name):
            raise ValidationError(
                _(
                    "At leaset first name or last name is required.",
                )
            )
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(
                _(
                    "User with the this phone number already exists. Please use a different phone number."
                )
            )
        return super().validate(attrs)

    def create_user(self, **kwargs):
        user: CustomUser = self.save(is_active=False, **kwargs)
        user.set_password(self.validated_data["password"])
        user.save()
        send_sms(
            message=f"Your VIBE account activation token is {user.activation_otp}.\nPlease do not share this token with any third party.",
            recipients=[user.phone_number],
        )
        return user


class UserActivationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=14)
    otp = serializers.CharField(max_length=4)

    def validate_phone_number(self, phone_number):
        validate_phonenumber(phone_number)
        if not CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_("User with the this phone number does not exist."))
        return phone_number

    def validate_otp(self, otp: str):
        if len(otp) != 4 or not otp.isdigit():
            raise ValidationError(_("otp must contain 4 digits"))
        return otp

    def validate(self, attrs: Dict):
        phone_number = attrs["phone_number"]
        otp = attrs["otp"]
        account: CustomUser = CustomUser.objects.filter(
            phone_number=phone_number
        ).first()
        if not account:
            raise ValidationError(_("User with the this phone number does not exist."))
        if account.activation_otp != otp:
            raise ValidationError(_("Invalid OTP code."))
        return attrs

    def activate(self):
        data = self.validated_data
        phone_number = data["phone_number"]
        otp = data["otp"]
        account: CustomUser = CustomUser.objects.filter(
            phone_number=phone_number
        ).first()
        if not account:
            raise ValidationError(_("User with the this phone number does not exist."))
        if account.activation_otp == otp:
            account.is_active = True
            account.save()
            return account
        raise ValidationError(_("Account activation failed."))


class ResendAccountTokenSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=14)

    def validate_phone_number(self, phone_number):
        validate_phonenumber(phone_number)
        if not CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError(_("User with the this phone number does not exist."))
        return phone_number

    def send_token(self):
        phone_number = self.validated_data["phone_number"]
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if not user:
            raise ValidationError(_("User with the this phone number does not exist."))
        send_sms(
            message=f"Your VIBE account activation token is {user.activation_otp}.\nPlease do not share this token with any third party.",
            recipients=[user.phone_number],
        )


class EmailEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def save(self, **kwargs):
        result = super().save(
            token=self.get_verification_token(),
            token_reason=CustomUser.TokenReason.EMAILVERIFICATION,
            **kwargs,
        )

    def get_verification_token(self, length=4):
        token = "".join([secrets.choice("0123456789") for i in range(length)])
        return token