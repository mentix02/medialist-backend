import random

import faker

from topic.models import Topic
from author.models import Author
from article.models import Article


fake = faker.Faker()


TOPIC_IDS = [topic[0] for topic in Topic.objects.values_list('id')]
AUTHOR_IDS = [author[0] for author in Author.objects.values_list('id')]


def create_article(draft: bool = random.random() > 0.8, **kwargs) -> Article:
    article = Article.objects.create(
        draft=draft,
        title=fake.text(50).title()[:-1],
        topic_id=kwargs.get('topic_id') or random.choice(TOPIC_IDS),
        author_id=kwargs.get('author_id') or random.choice(AUTHOR_IDS),
        content='\n\n'.join([fake.sentence(170) for _ in range(random.randint(7, 10))]),
    )
    return article
