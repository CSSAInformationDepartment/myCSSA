from django.core.cache import cache

from CommunityAPI import models


def get_favourite_count_for_post(post_id):
    """
    从本地内存中获取缓存的收藏数量。默认缓存 10 分钟。
    """
    key = 'favourite-count%d' % post_id

    if cache.has_key(key):
        return cache.get(key)

    else:
        count = models.FavouritePost.objects.filter(post_id=post_id).count()
        cache.set(key, count, 600)
        return count