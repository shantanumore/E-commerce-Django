from django.contrib import admin
from django.urls import path,include
from E_com import views

urlpatterns = [
    path("", views.index, name="E_com"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("productview/<int:myid>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("/pythonKit/handlerequest/",views.handlerequest , name="HandleRequest")

    
]
