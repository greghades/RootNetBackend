from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CodesVerification, CustomUser


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"  # Usa email como campo de autenticación

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name")


class UserTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "first_name", "last_name")




class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"].lower(),
            email=validated_data["email"].lower(),
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        return user


class ValidateCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodesVerification
        exclude = ("id",)
