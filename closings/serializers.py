from rest_framework import serializers

from .models import Deal, Document, Signature


class DealSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deal
        fields = ["id", "name", "status", "created_at"]  # noqa: RUF012


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "title", "status", "deal"]


class SignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Signature
        fields = ["id", "signed_at", "document", "signer"]