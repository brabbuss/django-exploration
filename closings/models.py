from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.


class Deal(models.Model): # pass parent - fields are declared on the class, not in a constructor
    # django adds 'id' primary key automatically
    class Status(models.TextChoices): # enum - value, display label
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): # self is explicit in py vs ts implicit this
        return self.name


class Document(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OUT_FOR_SIGNATURE = "out_for_signature", "Out For Signature"
        SIGNED = "signed", "Signed"

    title = models.CharField(max_length=200)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    # 'related_name' allows access from the other side, eg. deal.documents.all()
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="documents")

    def __str__(self):
        return self.title


class Signer(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField() # has max default
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="signers")

    def __str__(self):
        # f"..." is a template literal - {x} no need for $
        return f"{self.name} <{self.email}>"


# - `Signature`: joins a Document and a Signer, with a nullable `signed_at`. Add a
#   unique constraint on (document, signer).


class Signature(models.Model):
    signed_at = models.DateTimeField(null=True, blank=True)
    # should both belong to the same Deal
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="signatures")
    # PROTECT, not CASCADE: deleting a signer who has signatures raises
    # ProtectedError, so a record of who signed what can't vanish as a side
    # effect. Deleting the Document or the Deal still cascades.
    signer = models.ForeignKey(Signer, on_delete=models.PROTECT, related_name="signatures")

    # convention is fields then meta then methods
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["document", "signer"], name="one_signature_per_signer")
        ]

    def __str__(self):
        return f"{self.signer.name} on {self.document.title}"

    def clean(self):
        # Enforces "document and signer belong to the same deal".
        # clean() runs as part of full_clean(), which the admin and ModelForms
        # call. It does NOT run on save() or objects.create(), so API code has
        # to call full_clean() itself or repeat this check in the serializer.
        # The _id checks skip the rule while either side is still unset.
        if self.document_id and self.signer_id and self.document.deal_id != self.signer.deal_id:
            raise ValidationError("Document and signer must belong to the same deal.")
