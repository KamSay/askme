from django.http import JsonResponse
from django.urls import reverse
from urllib.parse import urlencode

from django.views.generic import TemplateView, DetailView, View

from .models import Question, Profile, Tag, Answer, QuestionLike
from app.util import get_paginator_range
from django.views.generic import ListView
from .forms import LoginForm, RegistrationForm, AskForm, SettingsForm, AnswerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, get_object_or_404
from django.db import models


PAGINATOR_MAX_LENGTH = 5


class BaseQuestionListView(ListView):
    model = Question
    template_name = 'app/index.html'
    context_object_name = 'questions'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_page = context['page_obj'].number
        total_pages = context['paginator'].num_pages
        context['paginator_range'] = get_paginator_range(PAGINATOR_MAX_LENGTH, current_page, total_pages)


        params = dict(self.request.GET.copy())
        if 'page' in params:
            params.pop('page')
        context['url_params'] = urlencode(params, doseq=True)

        questions = list(context["page_obj"].object_list)

        if self.request.user.is_authenticated and questions:
            qids = [q.id for q in questions]
            votes = dict(
                QuestionLike.objects
                .filter(user=self.request.user, question_id__in=qids)
                .values_list("question_id", "value")  # value: 1 / -1
            )
        else:
            votes = {}

        for q in questions:
            q.user_vote = votes.get(q.id)  # 1 / -1 / None

        context["questions"] = questions
        return context


class NewQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.new()


class HotQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.hot()


class AskView(TemplateView):
    template_name = "app/ask.html"

    def get(self, request, *args, **kwargs):
        form = AskForm()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = AskForm(request.POST)

        if form.is_valid():
            question = Question.objects.create(
                author=request.user,
                title=form.cleaned_data["title"],
                text=form.cleaned_data["text"],
            )

            tag_names = form.cleaned_data["tags"]
            tags = [Tag.objects.get_or_create(name=name)[0] for name in tag_names]
            if tags:
                question.tags.add(*tags)

            return redirect('app:question', pk=question.pk)

        return self.render_to_response(self.get_context_data(form=form))





class IndexView(BaseQuestionListView):
    template_name = 'app/index.html'

    def get_queryset(self):
        return Question.objects.all()


class IndexTagView(BaseQuestionListView):
    template_name = 'app/index_tag.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = self.request.GET.getlist('tag')
        return context

    def get_queryset(self):
        tags = self.request.GET.getlist('tag')
        return Question.objects.with_tags(tags)



class LoginView(TemplateView):
    template_name = "app/login.html"

    def get(self, request, *args, **kwargs):
        form = LoginForm(request=request)
        return self.render_to_response(self.get_context_data(
            form=form,
            continue_url=request.GET.get("continue", "/"),
        ))

    def post(self, request, *args, **kwargs):
        continue_url = request.GET.get("continue", "/")
        form = LoginForm(request.POST, request=request)

        if form.is_valid():
            login(request, form.cleaned_data["user"])
            return redirect(continue_url)

        return self.render_to_response(self.get_context_data(
            form=form,
            continue_url=continue_url,
        ))


class QuestionView(DetailView):
    model = Question
    template_name = "app/question.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        question = self.object
        context["answers"] = question.answers.all()
        context["question"] = question
        context.setdefault("form", AnswerForm())

        user_vote = None
        if self.request.user.is_authenticated:
            user_vote = (
                QuestionLike.objects
                .filter(user=self.request.user, question=question)
                .values_list("value", flat=True)
                .first()
            )

        question.user_vote = user_vote  # 1 / -1
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)

        if form.is_valid():
            Answer.objects.create(
                author=request.user,
                question=self.object,
                text=form.cleaned_data["text"],
            )
            url = reverse("app:question", kwargs={"pk": self.object.pk})
            return redirect(f"{url}#end")

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class RegistrationView(TemplateView):
    template_name = "app/registration.html"

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            Profile.objects.create(
                user=user,
                avatar=form.cleaned_data['avatar'],
            )
            login(request, user)
            return redirect("/")

        return self.render_to_response(self.get_context_data(form=form))


class SettingsView(TemplateView):
    template_name = 'app/settings.html'

    def get(self, request, *args, **kwargs):
        form = SettingsForm()
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        form = SettingsForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']
            request.user.save()

            profile = request.user.profile
            avatar = form.cleaned_data.get('avatar')
            if avatar is not None:
                profile.avatar = avatar
                profile.save()
            return redirect('app:settings')

        return self.render_to_response(self.get_context_data(form=form))


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("/")


class QuestionVoteView(LoginRequiredMixin, View):
    def post(self, request, question_id: int):
        question = get_object_or_404(Question, pk=question_id)
        vote_type = request.POST.get("type")
        if vote_type == "like":
            value = 1
        elif vote_type == "dislike":
            value = -1
        else:
            return JsonResponse({"ok": False}, status=400)

        vote, created = QuestionLike.objects.get_or_create(
            user=request.user,
            question=question,
            defaults={"value": value},
        )

        diff = value
        if not created:
            if vote.value != value:
                diff = value - vote.value
                vote.value = value
                vote.save(update_fields=["value"])
            else:
                diff = -value
                value = None
                vote.delete()

        question.like_amount = question.like_amount + diff
        question.save(update_fields=["like_amount"])

        return JsonResponse({"ok": True, "rating": question.like_amount, "user_vote": value})
