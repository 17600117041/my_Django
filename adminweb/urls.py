from django.conf.urls import url
from . import views
urlpatterns = [
    #登陆
    url(r'^admin/index$', views.index),
    url(r'^admin/admin$', views.admin),

    # 验证码
    url(r'^admin/get_code$', views.get_code),

    url(r'admin/ajax_login$', views.ajax_login),
    url(r'admin/ajax_logout$', views.ajax_logout),
    url(r'admin/ajax_menu_list', views.ajax_menu_list),
    url(r'admin/ajax_admin_list', views.ajax_admin_list),
    url(r'admin/ajax_admin_add', views.ajax_admin_add),
    url(r'admin/ajax_admin_del', views.ajax_admin_del),
    url(r'admin/ajax_admin_updatepwd$', views.ajax_admin_updatepwd),
    url(r'admin/ajax_dataclass_list$', views.ajax_dataclass_list),
    url(r'admin/ajax_dataclass_add', views.ajax_dataclass_add),
    url(r'admin/ajax_dataclass_del', views.ajax_dataclass_del),
    url(r'admin/ajax_data_list', views.ajax_data_list),
    url(r'admin/ajax_data_get', views.ajax_data_get),
    url(r'admin/ajax_data_add', views.ajax_data_add),
    url(r'admin/ajax_data_del', views.ajax_data_del),
    url(r'admin/ajax_art_single_get', views.ajax_art_single_get),
    url(r'admin/ajax_art_single_update', views.ajax_art_single_update),
]