from django.contrib.auth import authenticate
from rest_framework import serializers
from users.models import CustomUser, Profile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from olcha.serializers import FavoriteSerializer



class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'phone_number', 'password', 'confirm_password')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'is_staff': self.user.is_staff,
        }

        return data

class ProfileSerializer(serializers.ModelSerializer):
    favorites = FavoriteSerializer(many=True, read_only=True, source='user.favorites')
    class Meta:
        model = Profile
        fields = '__all__'
