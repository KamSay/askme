from idlelib.pyparse import trans

from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.urls import reverse
from urllib.parse import urlencode

from django.views.generic import TemplateView, DetailView, View

from .models import Question, Profile, Tag, Answer, QuestionLike, AnswerLike
from app.util import get_paginator_range
from django.views.generic import ListView
from .forms import LoginForm, RegistrationForm, AskForm, SettingsForm, AnswerForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, get_object_or_404


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
            q.user_is_author = (q.author.pk == self.request.user.pk)

        context["questions"] = questions
        context["top_profiles"] = Profile.objects.top(5)
        return context


class NewQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.new()


class HotQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.hot()


class AskView(LoginRequiredMixin, TemplateView):
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
        answers = question.answers.all()
        context["question"] = question
        context.setdefault("form", AnswerForm())


        if self.request.user.is_authenticated and answers:
            aids = [a.id for a in answers]
            votes = dict(
                AnswerLike.objects
                .filter(user=self.request.user, answer_id__in=aids)
                .values_list("answer_id", "value")  # value: 1 / -1
            )
        else:
            votes = {}

        for a in answers:
            a.user_vote = votes.get(a.id)  # 1 / -1 / None
            a.user_is_author = (a.author.pk == self.request.user.pk)

        context["answers"] = answers

        user_vote = None
        if self.request.user.is_authenticated:
            user_vote = (
                QuestionLike.objects
                .filter(user=self.request.user, question=question)
                .values_list("value", flat=True)
                .first()
            )

        question.user_vote = user_vote  # 1 / -1
        question.user_is_author = (question.author.pk == self.request.user.pk)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = AnswerForm(request.POST)

        if not request.user.is_authenticated:
            return redirect('app:login')

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


class SettingsView(LoginRequiredMixin, TemplateView):
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
    @transaction.atomic
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

        Question.objects.filter(pk=question.pk).update(like_amount = F('like_amount') + diff)
        question.refresh_from_db(fields=['like_amount'])

        Profile.objects.filter(pk=question.author.pk).update(rating = F('rating') + diff)

        return JsonResponse({"ok": True, "rating": question.like_amount, "user_vote": value})


class AnswerVoteView(LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, answer_id: int):
        answer = get_object_or_404(Answer, pk=answer_id)
        vote_type = request.POST.get("type")
        if vote_type == "like":
            value = 1
        elif vote_type == "dislike":
            value = -1
        else:
            return JsonResponse({"ok": False}, status=400)

        vote, created = AnswerLike.objects.get_or_create(
            user=request.user,
            answer=answer,
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

        Answer.objects.filter(pk=answer.pk).update(like_amount=F('like_amount') + diff)
        answer.refresh_from_db(fields=['like_amount'])
        Profile.objects.filter(pk=answer.author.pk).update(rating=F('rating') + diff)

        return JsonResponse({"ok": True, "rating": answer.like_amount, "user_vote": value})


class AnswerCorrectView(LoginRequiredMixin, View):
    def post(self, request, question_id: int, answer_id: int):
        question = get_object_or_404(Question, pk=question_id)
        answer = get_object_or_404(Answer, pk=answer_id, question_id=question.id)

        if question.author_id != request.user.id:
            return JsonResponse({"ok": False, "error": "forbidden"}, status=403)

        is_correct = request.POST.get("is_correct")

        if is_correct == "true":
            answer.is_correct = True
            answer.save(update_fields=["is_correct"])
            return JsonResponse({"ok": True})
        elif is_correct == "false":
            answer.is_correct = False
            answer.save(update_fields=["is_correct"])
            return JsonResponse({"ok": True})
        else:
            return JsonResponse({"ok": False, "error": "bad_request"}, status=400)