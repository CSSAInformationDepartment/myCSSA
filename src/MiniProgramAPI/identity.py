from CommunityAPI.models import UserInformation

from .models import MiniProgramProfile


def profile_identity(profile):
    try:
        mini_profile = profile.mini_program_profile
    except MiniProgramProfile.DoesNotExist:
        mini_profile = None
    try:
        community_profile = profile.userinformation
    except UserInformation.DoesNotExist:
        community_profile = None

    nickname = ''
    avatar = ''
    college = ''
    if mini_profile:
        nickname = mini_profile.nickname
        avatar = mini_profile.avatar_url
        college = mini_profile.college
    if community_profile:
        nickname = nickname or community_profile.username
        avatar = avatar or community_profile.avatarUrl

    nickname = nickname or profile.get_full_CN_name() or profile.get_full_EN_name() or '用户'
    if not avatar and profile.avatar:
        avatar = profile.avatar.url

    return {
        'userId': str(profile.pk),
        'nickname': nickname,
        'avatar': avatar or None,
        'college': college,
    }


def public_user_summary(profile, anonymous=False):
    if anonymous:
        return {
            'userId': None,
            'nickname': '匿名用户',
            'avatar': None,
            'isAnonymous': True,
        }

    if profile is None:
        return {
            'userId': None,
            'nickname': '已注销用户',
            'avatar': None,
            'isAnonymous': False,
        }

    identity = profile_identity(profile)
    return {
        'userId': identity['userId'],
        'nickname': identity['nickname'],
        'avatar': identity['avatar'],
        'isAnonymous': False,
    }
