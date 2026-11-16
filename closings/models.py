from django.db import models

# Create your models here.
### 1. Models, migrations, admin (about 1 hour) – `closings/models.py`, `closings/admin.py`

# - `Deal`: name, status, created timestamp.
# - `Document`: belongs to a Deal, title, status (`draft` → `out_for_signature` →
#   `signed`). Use `models.TextChoices` for the status.
# - `Signer`: belongs to a Deal, name, email.
# - `Signature`: joins a Document and a Signer, with a nullable `signed_at`. Add a
#   unique constraint on (document, signer).
# - Register all four in the admin and create a few rows by hand.

# Worth noticing: what `makemigrations` generates, what `related_name` gives you, and
# how a query count changes with `select_related` and `prefetch_related`.

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