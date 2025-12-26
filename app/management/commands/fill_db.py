from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from app import models
from datetime import datetime, timedelta
import random

from app.models import Profile, Question, QuestionLike, Answer, AnswerLike

BATCH_SIZE = 1000
MAX_LIKES = 500
MAX_ANSWERS = 5
MAX_TAGS = 20


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    seconds = delta.total_seconds()
    return start + timedelta(seconds=random.randint(0, int(seconds)))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, default=10,
                            help='Коэффициент заполнения (по умолчанию 10_')

    def handle(self, *args, **options):
        ratio = options['ratio']

        password_hash = make_password('12345678')
        users = [
            User(username=f'user_{i}', password=password_hash)
            for i in range(ratio)
        ]

        profiles = []
        User.objects.bulk_create(users, batch_size=BATCH_SIZE)
        for i, user in enumerate(users):
            profile = models.Profile(user=user)
            profiles.append(profile)

        active_profiles = users[:1500]


        tags = []
        for i in range(MAX_TAGS):
            tag = models.Tag(name=f'tag_{i}')
            tag.save()
            tags.append(tag)


        questions = []
        question_likes = []
        answers = []
        answer_likes = []
        for i in range(ratio * 10 + 1):
            if (i % 1000) == 0:
                print(i)

            like_amount = 0
            answer_count = 0
            if random.random() < 0.05:
                like_amount = random.randint(0, MAX_LIKES)
                answer_count = random.randint(0, MAX_ANSWERS)

            created_date = random_datetime(datetime(2020, 12, 16),
                                                                  datetime(2025, 12, 16))
            author = random.choice(active_profiles)
            author.profile.rating += like_amount
            question = models.Question(author=author,
                                       title=f'question_{i}?',
                                       text=f'question_text_{i}',
                                       created_at=created_date,
                                       like_amount=like_amount)
            questions.append(question)

            profiles_1 = random.sample(active_profiles, like_amount)
            for j in range(like_amount):
                question_likes.append(models.QuestionLike(user=profiles_1[j],
                                    question=question, value=1))
            for j in range(answer_count):
                like_amount = int(random.random() * min(ratio, 100))
                author = random.choice(active_profiles)
                author.profile.rating += like_amount
                answer = models.Answer(author=author,
                                       question=question,
                                       text=f'answer_{j}',
                                       created_at=random_datetime(created_date,
                                                                  datetime(2025, 12, 16)),
                                       like_amount=like_amount)
                answers.append(answer)

                profiles_1 = random.sample(active_profiles, like_amount)
                for j in range(like_amount):
                    answer_likes.append(models.AnswerLike(user=profiles_1[j], answer=answer, value=1))


            if len(questions) > 5000:
                Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)
                QuestionLike.objects.bulk_create(question_likes, batch_size=BATCH_SIZE)
                Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
                AnswerLike.objects.bulk_create(answer_likes, batch_size=BATCH_SIZE)
                questions.clear()
                question_likes.clear()
                answers.clear()
                answer_likes.clear()

        Question.objects.bulk_create(questions, batch_size=BATCH_SIZE)
        QuestionLike.objects.bulk_create(question_likes, batch_size=BATCH_SIZE)
        Answer.objects.bulk_create(answers, batch_size=BATCH_SIZE)
        AnswerLike.objects.bulk_create(answer_likes, batch_size=BATCH_SIZE)
        print(len(profiles))
        Profile.objects.bulk_create(profiles, batch_size=BATCH_SIZE)

        QuestionTag = Question.tags.through
        question_tags = []
        for question in questions:
            tag_amount = int(random.random() * random.random() * random.random() * 7)
            chosen_tags = random.sample(tags, tag_amount)
            for tag in chosen_tags:
                question_tags.append(QuestionTag(question_id=question.id, tag_id=tag.id))
        QuestionTag.objects.bulk_create(question_tags, batch_size=BATCH_SIZE)

