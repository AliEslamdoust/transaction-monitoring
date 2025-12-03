from django.urls import path
from . import views

urlpatterns = [
    path("add-transaction/", views.ObtainTransactionDetailsView.as_view()),
    path(
        "delete-transactions/",
        views.DeleteTransactionsView.as_view(),
    ),
    path("get-transactions", views.GetTransactionsAverageView.as_view()),
    path("get-transaction/<int:pk>", views.gettransaction.as_view()),
]
