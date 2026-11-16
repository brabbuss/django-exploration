from rest_framework.routers import DefaultRouter

from .views import DealViewSet, DocumentViewSet, SignatureViewSet

router = DefaultRouter()
router.register("deals", DealViewSet)
router.register("documents", DocumentViewSet)
router.register("signatures", SignatureViewSet)

urlpatterns = router.urls