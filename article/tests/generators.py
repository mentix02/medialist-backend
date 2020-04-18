import random
import typing

import faker

from topic.models import Topic
from author.models import Author
from article.models import Article


fake = faker.Faker()

THUMBNAIL_URL_IDs = (
    '557',
    '251',
    '700',
    '420',
    '1000'
)

TAGS = ['idea', 'good', 'west', 'animal', 'foot', 'for', 'time', 'hello']
TOPIC_IDS = [topic[0] for topic in Topic.objects.values_list('id')]
AUTHOR_IDS = [author[0] for author in Author.objects.values_list('id')]


def create_article(draft: bool = random.random() > 0.93, **kwargs) -> Article:

    def _random_tags() -> typing.List[str]:
        nums = random.randint(2, len(TAGS) - 1)
        return list({random.choice(TAGS) for _ in range(nums)})

    try:
        article = Article.objects.create(
            draft=draft,
            title=fake.text(50).title()[:-1],
            topic_id=kwargs.get('topic_id') or random.choice(TOPIC_IDS),
            author_id=kwargs.get('author_id') or random.choice(AUTHOR_IDS),
            content='\n\n'.join([fake.sentence(170) for _ in range(random.randint(7, 10))]),
        )
    except IndexError:
        print('Create some topics first.')
    else:
        article.set_tags_from_string(','.join(_random_tags()))
        return article
