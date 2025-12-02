from django.urls import path
from .views import ObtainTransactionDetailsView

urlpatterns = [
    path("add-transaction/",ObtainTransactionDetailsView.as_view())
]
