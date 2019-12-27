from topic.models import Topic


def topic_slug_is_available(slug: str) -> bool:
    try:
        Topic.objects.get(slug__iexact=slug)
    except Topic.DoesNotExist:
        return True
    else:
        return False
