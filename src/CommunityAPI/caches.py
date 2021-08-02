from cachetools import cached, TTLCache

from CommunityAPI import models

__favourite_count_cache = TTLCache(maxsize=1024*1024, ttl=60*10) # 8M, 10min
def get_favourite_count_for_post(post_id, detail=False):
    """
    从本地内存中获取缓存的收藏数量。默认缓存 10 分钟。
    
    如果 detail == True，强制刷新缓存
    """

    if post_id in __favourite_count_cache and not detail:
        return __favourite_count_cache[post_id]

    count = models.FavouritePost.objects.filter(post_id=post_id).count()
    __favourite_count_cache[post_id] = count
    return count