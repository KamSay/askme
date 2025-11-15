from urllib.parse import urlencode

from django.views.generic import TemplateView, DetailView

from .models import Question
from app.util import get_paginator_range
from django.views.generic import ListView


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
        return context


class NewQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.new()


class HotQuestionListView(BaseQuestionListView):
    def get_queryset(self):
        return Question.objects.hot()


class AskView(TemplateView):
    template_name = 'app/ask.html'


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
    template_name = 'app/login.html'


class QuestionView(DetailView):
    model = Question
    template_name = 'app/question.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['answers'] = self.object.answers.all()
        return context


class RegistrationView(TemplateView):
    template_name = 'app/registration.html'


class SettingsView(TemplateView):
    template_name = 'app/settings.html'


