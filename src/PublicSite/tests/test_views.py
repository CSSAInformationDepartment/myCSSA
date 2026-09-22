
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from myCSSAhub.models import DiscountMerchant
from RecruitAPI.models import JobList
from UserAuthAPI.models import CSSADept


'''
======================= Instructions of performing views unit tests =======================
1. set up a method named test_[views name]_[HTTP Method Name]

2. following the samples below to fill the internal code

3. 


Video Reference: https://www.youtube.com/watch?v=hA_VxnxCHbo
==========================================================================================
'''


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        return super().setUp()

    def test_events_list_GET(self):
        response = self.client.get(reverse('PublicSite:events'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'PublicSite/event.html')
        self.assertContains(response, 'CAMPUS LIFE IN MOTION')
        self.assertContains(response, '活动消息')
        self.assertContains(response, '新活动正在筹备中')

    def test_contact_page_lists_social_channels_and_helpers_in_order(self):
        response = self.client.get(reverse('PublicSite:contact'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'PublicSite/contact_us.html')
        content = response.content.decode('utf-8')
        ordered_labels = [
            '抖音',
            '小红书',
            '微信公众号',
            'CSSA 小助手 3号',
            'CSSA 小助手 4号',
            'CSSA 小助手 5号',
            'CSSA 小助手 6号',
        ]
        positions = [content.index(label) for label in ordered_labels]
        self.assertEqual(positions, sorted(positions))
        self.assertContains(response, 'contact-douyin.jpg')
        self.assertContains(response, 'contact-xiaohongshu.jpg')
        self.assertContains(response, 'GET IN TOUCH')

    def test_department_page_uses_shared_brand_hero(self):
        response = self.client.get(
            reverse('PublicSite:departments', args=['information'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'cssa-page-hero cssa-department-hero')
        self.assertContains(response, 'MEET THE TEAM')
        self.assertContains(response, 'Department of Information Technology')

    def test_merchants_page_filters_search_and_category(self):
        DiscountMerchant.objects.create(
            merchant_name='Alpha Noodles',
            merchant_description='Insider 九折',
            merchant_address='Melbourne CBD',
            merchant_image='img/merchants/alpha.png',
            merchant_type='折扣商家',
            merchant_Category='餐饮美食',
        )
        DiscountMerchant.objects.create(
            merchant_name='Beta Market',
            merchant_description='购物优惠',
            merchant_address='Carlton',
            merchant_image='img/merchants/beta.png',
            merchant_type='折扣商家',
            merchant_Category='消费购物',
        )

        response = self.client.get(
            reverse('PublicSite:merchants'),
            {'q': 'Alpha', 'category': '餐饮美食'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Alpha Noodles')
        self.assertNotContains(response, 'Beta Market')
        self.assertContains(response, 'CSSA INSIDER BENEFITS')
        self.assertContains(response, 'Insider 专属优惠')
        self.assertEqual(response.context['page_obj'].paginator.count, 1)

    def test_merchants_page_paginates_twelve_cards(self):
        for index in range(13):
            DiscountMerchant.objects.create(
                merchant_name='Merchant {}'.format(index),
                merchant_description='Insider 优惠',
                merchant_address='Melbourne',
                merchant_image='img/merchants/{}.png'.format(index),
                merchant_type='折扣商家',
                merchant_Category='生活服务',
            )

        response = self.client.get(reverse('PublicSite:merchants'), {'page': 2})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)
        self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_merchants_page_has_empty_state(self):
        response = self.client.get(reverse('PublicSite:merchants'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '合作商家正在更新中')

    def test_sponsor_page_groups_ranked_and_unclassified_partners(self):
        DiscountMerchant.objects.create(
            merchant_name='Diamond Partner',
            merchant_description='钻石合作伙伴介绍',
            merchant_address='Melbourne',
            merchant_image='img/merchants/diamond.png',
            merchant_type='赞助商家',
            merchant_level='钻石商家',
        )
        DiscountMerchant.objects.create(
            merchant_name='Community Partner',
            merchant_description='社区合作伙伴介绍',
            merchant_address='Carlton',
            merchant_image='img/merchants/community.png',
            merchant_type='赞助商家',
            merchant_level=None,
        )

        response = self.client.get(reverse('PublicSite:supportMerchants'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Diamond Partner')
        self.assertContains(response, 'Community Partner')
        self.assertContains(response, '钻石合作伙伴')
        self.assertContains(response, '合作伙伴')
        self.assertEqual(response.context['sponsor_count'], 2)

    def test_sponsor_page_has_empty_state(self):
        response = self.client.get(reverse('PublicSite:supportMerchants'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '赞助商资料正在更新中')

    def test_recruitment_page_lists_all_active_jobs_without_filters(self):
        information = CSSADept.objects.create(
            deptName='information',
            deptTitle='信息部',
            deptTitleEN='Information Technology',
        )
        publicity = CSSADept.objects.create(
            deptName='publicity',
            deptTitle='宣传部',
            deptTitleEN='Publicity',
        )
        JobList.objects.create(
            dept=information,
            jobName='网站开发成员',
            description='参与 CSSA 官网开发与维护',
            dueDate=timezone.now() + timezone.timedelta(days=14),
        )
        JobList.objects.create(
            dept=publicity,
            jobName='视觉设计成员',
            description='负责活动视觉设计',
            dueDate=timezone.now() + timezone.timedelta(days=14),
        )

        response = self.client.get(reverse('PublicSite:recruitment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '网站开发成员')
        self.assertContains(response, '视觉设计成员')
        self.assertContains(response, '持续招募', count=2)
        self.assertNotContains(response, 'job-search')
        self.assertEqual(response.context['page_obj'].paginator.count, 2)

    def test_recruitment_page_keeps_expired_legacy_job_open(self):
        department = CSSADept.objects.create(
            deptName='academic',
            deptTitle='学术部',
            deptTitleEN='Academic',
        )
        JobList.objects.create(
            dept=department,
            jobName='过期测试岗位',
            description='用于确认截止状态',
            dueDate=timezone.now() - timezone.timedelta(days=1),
        )

        response = self.client.get(reverse('PublicSite:recruitment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '过期测试岗位')
        self.assertContains(response, '持续招募')
        self.assertContains(response, '申请岗位')
        self.assertNotContains(response, '申请已截止')

    def test_recruitment_page_has_empty_state(self):
        response = self.client.get(reverse('PublicSite:recruitment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '新一轮招募正在筹备中')

    # def test_events_detail_GET(self):
    #     response = self.client.get(reverse('PublicSite:eventsDetails', args=[]))
    #     self.assertEquals(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'PublicSite/eventDetails.html')
