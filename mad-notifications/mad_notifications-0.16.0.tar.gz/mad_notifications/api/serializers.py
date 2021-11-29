from mad_notifications.models import Device, Notification
from rest_framework import serializers



class DeviceSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=255, required=True)
    class Meta:
        model = Device
        fields = (
            'id',
            'user',
            'token',

            'created_at', 'updated_at',
            'url',
        )

        read_only_fields = ('user',)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'id',
            'user',
            'title',
            'content',
            'is_read',
            'icon',
            'image',
            "data",
            "actions",

            'created_at', 'updated_at',
            'url',
        )
        read_only_fields = fields
