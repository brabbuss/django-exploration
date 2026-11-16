from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Deal, Document, Signature
from .serializers import DealSerializer, DocumentSerializer, SignatureSerializer

# Create your views here.


class DealViewSet(viewsets.ModelViewSet):
    queryset = Deal.objects.all()
    serializer_class = DealSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer


class SignatureViewSet(viewsets.ModelViewSet):
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer

    @action(detail=True, methods=["post"])
    def sign(self, request, pk=None):
        with transaction.atomic():
            signature: Signature = self.get_object()
            document = Document.objects.select_for_update().get(pk=signature.document_id)
            # need the signature to get the doc id, to get the lock, so refresh after the lock
            signature.refresh_from_db()
            if signature.signed_at is not None:
                return Response({"detail": "Signature already signed."}, status=400)
            
            signature.signed_at = timezone.now()
            signature.save()

            has_unsigned = document.signatures.filter(signed_at__isnull=True).exists()
            if not has_unsigned:
                document.status = Document.Status.SIGNED
                document.save()
            return Response(self.get_serializer(signature).data)