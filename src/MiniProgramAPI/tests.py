import uuid
from unittest.mock import patch

from django.test import override_settings
from rest_framework.test import APITestCase

from CommunityAPI.models import Post
from UserAuthAPI.models import User, UserProfile

from .constants import AUDIT_APPROVED
from .models import (
    Course,
    CourseReview,
    InteractionMessage,
    MiniProgramProfile,
    PostExtension,
    PostLike,
)


@override_settings(
    MINIPROGRAM_CONTENT_AUDIT_REQUIRED=False,
    MINIPROGRAM_IMAGE_AUDIT_REQUIRED=False,
)
class MiniProgramAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='author@example.test',
            telNumber='0400000001',
            password='test-password',
        )
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            firstNameEN='Author',
            lastNameEN='One',
            studentId='1000000001',
        )
        cls.other_user = User.objects.create_user(
            email='reader@example.test',
            telNumber='0400000002',
            password='test-password',
        )
        cls.other_profile = UserProfile.objects.create(
            user=cls.other_user,
            firstNameEN='Reader',
            lastNameEN='Two',
            studentId='1000000002',
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user=user or self.user)

    def create_post(self, **overrides):
        self.authenticate()
        payload = {
            'section': 1,
            'title': '测试帖子',
            'content': '用于自动化测试的正文',
            'imageIds': [],
            'isAnonymous': False,
        }
        payload.update(overrides)
        response = self.client.post('/api/v1/posts', payload, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        return int(response.json()['data']['postId'])

    def test_health_uses_envelope_and_request_id(self):
        request_id = str(uuid.uuid4())
        response = self.client.get(
            '/api/v1/health',
            HTTP_X_REQUEST_ID=request_id,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            'code': 0,
            'message': 'ok',
            'data': {'status': 'ok'},
        })
        self.assertEqual(response['X-Request-Id'], request_id)

    def test_write_requires_authentication(self):
        response = self.client.post('/api/v1/posts', {}, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['code'], 10002)

    @patch('MiniProgramAPI.views.exchange_wechat_code')
    def test_authenticated_user_can_bind_wechat_without_exposing_openid(self, exchange):
        exchange.return_value = 'openid-author'
        self.authenticate()
        response = self.client.post(
            '/api/v1/auth/wechat-bind',
            {'code': 'temporary-wx-code'},
            format='json',
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(response.json()['data']['wechatBound'])
        self.assertNotIn('openid', response.content.decode().lower())
        self.assertEqual(
            MiniProgramProfile.objects.get(user=self.profile).wechat_openid,
            'openid-author',
        )

    @patch('MiniProgramAPI.views.exchange_wechat_code')
    def test_wechat_identity_cannot_bind_two_cssanet_accounts(self, exchange):
        exchange.return_value = 'openid-existing'
        MiniProgramProfile.objects.create(
            user=self.profile,
            wechat_openid='openid-existing',
        )
        self.authenticate(self.other_user)
        response = self.client.post(
            '/api/v1/auth/wechat-bind',
            {'code': 'temporary-wx-code'},
            format='json',
        )
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['code'], 10005)
        self.assertFalse(
            MiniProgramProfile.objects.filter(user=self.other_profile).exists()
        )

    def test_post_creation_is_idempotent_and_public(self):
        self.authenticate()
        key = str(uuid.uuid4())
        payload = {
            'title': '幂等发布',
            'content': '同一个 key 只能创建一次',
            'isAnonymous': True,
        }
        first = self.client.post(
            '/api/v1/posts', payload, format='json', HTTP_IDEMPOTENCY_KEY=key,
        )
        second = self.client.post(
            '/api/v1/posts', payload, format='json', HTTP_IDEMPOTENCY_KEY=key,
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(first.json()['data'], second.json()['data'])
        self.assertEqual(Post.objects.filter(replyToId__isnull=True).count(), 1)

        self.client.force_authenticate(user=None)
        listing = self.client.get('/api/v1/posts')
        item = listing.json()['data']['list'][0]
        self.assertEqual(item['author']['nickname'], '匿名用户')
        self.assertIsNone(item['author']['userId'])
        self.assertFalse(item['isLiked'])

    def test_post_rate_limit_returns_retry_after(self):
        self.create_post()
        response = self.client.post('/api/v1/posts', {
            'title': '第二帖',
            'content': '发布间隔不足一分钟',
        }, format='json')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()['code'], 10007)
        self.assertGreaterEqual(response.json()['data']['retryAfter'], 1)

    @patch('MiniProgramAPI.views.audit_text')
    def test_rejected_post_idempotency_replays_422_without_duplicate(self, audit):
        audit.return_value = ('REJECTED', '内容未通过安全审核')
        self.authenticate()
        key = str(uuid.uuid4())
        payload = {'title': '审核测试', 'content': '需要拒绝的内容'}
        first = self.client.post(
            '/api/v1/posts', payload, format='json', HTTP_IDEMPOTENCY_KEY=key,
        )
        second = self.client.post(
            '/api/v1/posts', payload, format='json', HTTP_IDEMPOTENCY_KEY=key,
        )
        self.assertEqual(first.status_code, 422)
        self.assertEqual(second.status_code, 422)
        self.assertEqual(first.json(), second.json())
        self.assertEqual(Post.objects.filter(replyToId__isnull=True).count(), 1)
        self.assertEqual(
            InteractionMessage.objects.filter(recipient=self.profile).count(),
            1,
        )

    def test_comment_reply_and_delete_keep_cached_count_consistent(self):
        post_id = self.create_post()
        self.authenticate(self.other_user)
        comment = self.client.post(
            '/api/v1/posts/{}/comments'.format(post_id),
            {'content': '一级评论'},
            format='json',
        )
        self.assertEqual(comment.status_code, 201, comment.content)
        comment_id = int(comment.json()['data']['commentId'])
        reply = self.client.post(
            '/api/v1/posts/{}/comments'.format(post_id),
            {
                'content': '二级回复',
                'rootId': str(comment_id),
                'replyToCommentId': str(comment_id),
            },
            format='json',
        )
        self.assertEqual(reply.status_code, 201, reply.content)
        PostExtension.objects.get(post_id=post_id).refresh_from_db()
        extension = PostExtension.objects.get(post_id=post_id)
        self.assertEqual(extension.comment_count, 2)

        listing = self.client.get('/api/v1/posts/{}/comments'.format(post_id))
        item = listing.json()['data']['list'][0]
        self.assertEqual(item['replyCount'], 1)
        self.assertEqual(len(item['replies']), 1)

        self.authenticate()
        deleted = self.client.delete('/api/v1/comments/{}'.format(comment_id))
        self.assertEqual(deleted.status_code, 200)
        extension.refresh_from_db()
        self.assertEqual(extension.comment_count, 0)

    def test_like_toggle_is_state_based_and_creates_one_message(self):
        post_id = self.create_post()
        self.authenticate(self.other_user)
        payload = {'targetType': 1, 'targetId': str(post_id), 'liked': True}
        first = self.client.post('/api/v1/likes/toggle', payload, format='json')
        second = self.client.post('/api/v1/likes/toggle', payload, format='json')
        self.assertEqual(first.json()['data']['likeCount'], 1)
        self.assertEqual(second.json()['data']['likeCount'], 1)
        self.assertEqual(PostLike.objects.filter(post_id=post_id).count(), 1)
        self.assertEqual(
            InteractionMessage.objects.filter(recipient=self.profile).count(),
            1,
        )

        unlike = self.client.post('/api/v1/likes/toggle', {
            **payload,
            'liked': False,
        }, format='json')
        self.assertEqual(unlike.json()['data']['likeCount'], 0)

    def test_course_review_aggregates_duplicates_and_soft_delete(self):
        self.authenticate()
        course_payload = {
            'name': 'Algorithms',
            'code': 'COMP90001',
            'teacher': 'Ada Lovelace',
            'college': 'Engineering',
            'credit': '12.50',
        }
        created = self.client.post('/api/v1/courses', course_payload, format='json')
        self.assertEqual(created.status_code, 201, created.content)
        course_id = created.json()['data']['courseId']
        duplicate = self.client.post('/api/v1/courses', {
            **course_payload,
            'name': '  algorithms ',
            'teacher': 'ADA   LOVELACE',
        }, format='json')
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()['data']['courseId'], course_id)

        review = self.client.post(
            '/api/v1/courses/{}/reviews'.format(course_id),
            {'rating': 5, 'content': '讲解清晰', 'isAnonymous': False},
            format='json',
        )
        self.assertEqual(review.status_code, 201, review.content)
        review_id = review.json()['data']['reviewId']
        course = Course.objects.get(pk=course_id)
        self.assertEqual(course.review_count, 1)
        self.assertEqual(str(course.rating_average), '5.00')

        updated = self.client.put(
            '/api/v1/reviews/{}'.format(review_id),
            {'rating': 3, 'content': '更新后的评价', 'isAnonymous': True},
            format='json',
        )
        self.assertEqual(updated.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(str(course.rating_average), '3.00')

        deleted = self.client.delete('/api/v1/reviews/{}'.format(review_id))
        self.assertEqual(deleted.status_code, 200)
        course.refresh_from_db()
        self.assertEqual(course.review_count, 0)
        self.assertIsNotNone(CourseReview.objects.get(pk=review_id).deleted_at)

    def test_invalid_review_like_id_is_validation_error(self):
        self.authenticate()
        response = self.client.post('/api/v1/likes/toggle', {
            'targetType': 3,
            'targetId': 'not-a-uuid',
            'liked': True,
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 10001)

    def test_likes_given_cursor_is_opaque_and_tamper_protected(self):
        post_id = self.create_post()
        second_post = Post.objects.create(
            viewableToGuest=True,
            createdBy=self.other_profile,
        )
        PostExtension.objects.create(
            post=second_post,
            audit_status=AUDIT_APPROVED,
        )
        PostLike.objects.create(user=self.profile, post_id=post_id)
        PostLike.objects.create(user=self.profile, post=second_post)
        self.authenticate()
        first = self.client.get('/api/v1/users/me/likes/given?size=1')
        cursor = first.json()['data']['nextCursor']
        self.assertTrue(cursor)
        self.assertNotEqual(cursor, '1')
        second = self.client.get(
            '/api/v1/users/me/likes/given?size=1&cursor={}'.format(cursor)
        )
        self.assertEqual(second.status_code, 200)
        invalid = self.client.get(
            '/api/v1/users/me/likes/given?cursor={}x'.format(cursor)
        )
        self.assertEqual(invalid.status_code, 400)
