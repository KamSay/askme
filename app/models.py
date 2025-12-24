from urllib.parse import urlencode

from django.db import models
from django.contrib.auth.models import User


class QuestionQuerySet(models.QuerySet):
    def new(self):
        return self.order_by('-created_at')

    def hot(self):
        return self.order_by('-like_amount')

    def with_tags(self, tags):
        qs = self
        for tag in tags:
            qs = qs.filter(tags__name=tag)
        return qs


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/gray.png')

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar.name = 'avatars/gray.png'
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=40, unique=True)


class Question(models.Model):
    objects = QuestionQuerySet.as_manager()

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag)
    like_amount = models.PositiveIntegerField(default=0, db_index=True)

    def build_path(self):
        params = dict(self.request.GET.copy())
        if 'page' in params:
            params.pop('page')
        return urlencode(params, doseq=True)


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    like_amount = models.PositiveIntegerField(default=0, db_index=True)


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = ('user', 'answer')


