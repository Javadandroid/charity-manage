from django.contrib.auth.models import User, Group
from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    group_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser', 'groups', 'group_ids', 'password']

    def create(self, validated_data):
        group_ids = validated_data.pop('group_ids', [])
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        if group_ids:
            user.groups.set(Group.objects.filter(id__in=group_ids))
        return user

    def update(self, instance, validated_data):
        group_ids = validated_data.pop('group_ids', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if group_ids is not None:
            instance.groups.set(Group.objects.filter(id__in=group_ids))

        return instance
