from django.urls import path
from .views import (
    AskView,
    IndexView,
    IndexTagView,
    LoginView,
    QuestionView,
    RegistrationView,
    SettingsView,
    NewQuestionListView,
    HotQuestionListView,
)

app_name = "app"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("ask/", AskView.as_view(), name="ask"),
    path("tag/", IndexTagView.as_view(), name="tag"),
    path("login/", LoginView.as_view(), name="login"),
    path("question/<int:pk>/", QuestionView.as_view(), name="question"),
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("new/", NewQuestionListView.as_view(), name="new"),
    path("hot/", HotQuestionListView.as_view(), name="hot"),
]