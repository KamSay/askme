import random
import string



def generate_fish_questions(count: int):
    questions = []
    for i in range(count):
        questions.append({
            'rate': random.randint(-10, 10),
            'title': 'title ' + str(random.randint(1, 100000)),
            'text': ''.join([random.choice(string.ascii_letters + ' ' * 1) for i in range(random.randint(10, 500))]),
            'tags': {f'tag{i}' for i in range(1, random.randint(1, 5))}
        })
    return questions


IS_AUTHENTICATED = True
QUESTIONS_DATASET = generate_fish_questions(10)
