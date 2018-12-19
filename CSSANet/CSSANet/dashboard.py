"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'CSSANet.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a group for "Administration" & "Applications"
        self.children.append(modules.Group(
            _('账户组权限管理： Administration '),
            column=1,
            collapsible=True,
            children = [
                modules.AppList(
                    _('账户权限 Administration'),
                    column=1,
                    collapsible=False,
                    models=('django.contrib.*',),
                ),
            ]
        ))

        # append an app list module for "Applications"
        self.children.append(modules.AppList(
            _('数据表管理: Applications Data Management'),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))


        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('文件系统管理 Media Management'),
            column=2,
            children=[
                {
                    'title': _('文件管理器 FileBrowser'),
                    'url': '/admin/filebrowser/browse/',
                    'external': False,
                },
            ]
        ))


        # append a recent actions module
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            limit=5,
            collapsible=False,
            column=3,
        ))
