from cachetools import cached, TTLCache

from CommunityAPI import models


@cached(cache=TTLCache(maxsize=1024*1024, ttl=60*10)) # 1M, 10min
def get_favourite_count_for_post(post_id):
    """
    从本地内存中获取缓存的收藏数量。默认缓存 10 分钟。
    """
    return models.FavouritePost.objects.filter(post_id=post_id).count()