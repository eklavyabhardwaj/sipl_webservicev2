# configurator/urls.py
from django.urls import path
from .views import (
    GroupListView, QuizView, PageView, product_menu_api,
    CareerListView, CareerDetailView, CareerApplyView, CareerTermsView,
    ContactView, contact_thanks,
    GroupExploreView, ItemDetailView,  # keep ItemDetailView (we link to it)
    VariantBuilderView,                # builder page
)

app_name = "configurator"

urlpatterns = [
    # Pages / Home
    path("", PageView.as_view(), name="home"),
    path("pages/<slug:slug>/", PageView.as_view(), name="page"),

    # Quiz (group list + quiz-by-group)
    path("quiz/", GroupListView.as_view(), name="group_list"),
    path("quiz/<slug:slug>/", QuizView.as_view(), name="quiz"),
    path("quiz/<slug:slug>/explore/", GroupExploreView.as_view(), name="group_explore"),

    # Variant builder for a given group+item
    path("<slug:slug>/<int:item_id>/builder/", VariantBuilderView.as_view(), name="variant_builder"),

    # Item detail (we’ll link matches here, optionally with ?variant=<id>)
    path("item/<int:item_id>/", ItemDetailView.as_view(), name="item_detail"),

    # Careers
    path("careers/", CareerListView.as_view(), name="career_list"),
    path("careers/job/<str:job_id>/", CareerDetailView.as_view(), name="career_detail"),
    path("careers/apply/", CareerApplyView.as_view(), name="career_apply"),
    path("careers/terms/", CareerTermsView.as_view(), name="career_terms"),

    # Contact
    path("contact/", ContactView.as_view(), name="contact"),
    path("contact/thanks/", contact_thanks, name="contact_thanks"),

    # API
    path("api/product-menu/", product_menu_api, name="product_menu_api"),
]
