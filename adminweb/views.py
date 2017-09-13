from django.shortcuts import render
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseRedirect
import platform
import json
import time
import sys
import django
import os
from . import  cfg
from . import commons
from .models import Admin
from .models import ArtSingle
from .models import Data,DataClass
# Create your views here.
def index(request):
    # 需要登陆才可以
    if request.session.get("sess_admin", False):
        return HttpResponseRedirect('admin')
    return render(request,'adminweb/index.html')

def admin(request):
    #需要登陆才可以
    if not request.session.get("sess_admin", False):
        return HttpResponseRedirect('index')
    system = platform.uname()

    res_data = {
        'title' : cfg.web_name,
        'django_version' : django.get_version(),
        'python_version' : platform.python_version(),
        'system' : system[0] + " " + system[1],
    }

    return commons.render_template(request,'adminweb/admin.html',res_data)

def get_code(request):
    ca = commons.Captcha(request)
    # ca.words = ['hello', 'world', 'helloworld']
    ca.type = 'number'  # or word
    ca.img_width = 150
    ca.img_height = 30
    return ca.display()

def ajax_login(request):
    imgcode = request.GET.get("code")
    print(imgcode)
    if not imgcode or imgcode == '':
        return commons.res_fail(1, "验证码不能为空")
    ca = commons.Captcha(request)
    if ca.check(imgcode):
        name = request.GET.get("name")
        pwd = request.GET.get("pwd")
        # admin = Admin(name = name,pwd = pwd)
        # admin.save()
        try:
            admin = Admin.objects.get(name = name, pwd = pwd)
            admin_jsonstr = admin.toJSON()
            admin = json.loads(admin_jsonstr)

            del(admin["pwd"])
            request.session["sess_admin"] = admin
            return commons.res_success("登陆成功")
        except:
            return commons.res_fail(1,"用户或密码不正确！")
    else:
        return commons.res_fail(1, "验证码不正确")

def ajax_logout(request):
    #需要登录
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要先登陆")
    del request.session["sess_admin"]
    return commons.res_success("退出登录")

def ajax_menu_list(request):
    #需要登录
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录")
    return commons.res_success("请求成功", cfg.admin_menu_list)

def ajax_admin_list(request):
    #需要登录
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录")
    #分页搜索和每页显示数
    page = 1
    page_size = cfg.page_size
    if request.GET.get("page"):
        page = int(request.GET.get("page"))
    if request.GET.get("page_size"):
        page_size = int(request.GET.get("page_size"))
    res_data = Admin.getList(page, page_size)
    return commons.res_success("请求成功", res_data)

def ajax_admin_add(request):
    #需要登陆
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录")

    name = request.GET.get("name")
    pwd = request.GET.get("pwd")
    pwd2 = request.GET.get("pwd2")

    if name == "":
        return commons.res_fail(1, "用户名不能为空")
    if pwd == "":
        return commons.res_fail(1, "密码不能为空")
    if pwd != pwd2:
        return commons.res_fail(1, "确认密码不正确")

    total = Admin.objects.filter(name = name).count()
    if total > 1 :
        return commons.res_fail(1, "用户名已存在")

    admin = Admin(
        name = name,
        pwd = pwd,
        add_time = int(time.time())
    )
    admin.save()
    return commons.res_success("添加成功", json.loads(admin.toJSON()))

def ajax_admin_del(request):
    #需要登录
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录")
    id = request.GET.get("id")
    try:
        admin = Admin.objects.get(id=id)
        admin.delete()
        return commons.res_success("删除成功")
    except:
        return commons.res_fail(1, "该数据不存在")

def ajax_admin_updatepwd(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1,"需要登陆")
    curr_admin = request.session.get("sess_admin")
    # return commons.res_fail(11, curr_admin)
    old_pwd = request.GET.get("old_pwd")
    pwd = request.GET.get("pwd")
    pwd2 = request.GET.get("pwd2")

    if old_pwd == "":
        return commons.res_fail(1, "旧密码不能为空")
    if pwd == "":
        return commons.res_fail(1, "新密码不能为空")
    if pwd != pwd2:
        return commons.res_fail(1, "确认密码不正确")

    try:
        admin = Admin.objects.get(name = curr_admin["name"], pwd = pwd)
        admin.pwd = pwd
        admin.save()
        return commons.res_success("修改密码成功")
    except:
        return commons.res_fail(1, "旧密码不正确")

def ajax_dataclass_list(request):
    if not request.session.get("sess_admin", False):
        return commons.res_fail(1, "需要登录")
    type = int(request.GET.get("type"))
    dataclass_list = DataClass.objects.filter(type = type, parent_id = 0 ).order_by("-sort", "-id")
    dataclass_list_json = []
    for dataclass in dataclass_list:
        item = json.loads(dataclass.toJSON())

        child_count = DataClass.objects.filter(parent_id = item["id"]).count()
        if child_count > 0:
            item["children"] = DataClass.listById(item["id"])
        dataclass_list_json.append(item)
    return commons.res_success("请求成功", dataclass_list_json)

def ajax_dataclass_get(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")
    try:
        id = request.GET.get("id")
        dataclass = DataClass.objects.get(id = id)

        dataclass_json = json.loads(dataclass.toJSON())
        if dataclass_json["parent_id"] != 0:
            dataclass_json["parent"] = DataClass.getById(dataclass_json["parent_id"])

        return commons.res_success("请求成功", dataclass_json)
    except:
        return commons.res_fail(1, "找不到数据")

def ajax_dataclass_add(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")

    id = 0
    if request.GET.get("id"):
        id = int(request.GET.get("id"))

    name = request.GET.get("name")
    parent_id = int(request.GET.get("parent_id"))
    dataclass = None
    if id != 0:
        if id == parent_id:
            return commons.res_fail(1, "父级分类不能为当前选中分类")

        dataclass = DataClass.objects.get(id = id)
    else:
        dataclass = DataClass()

    dataclass.parent_id = parent_id
    dataclass.name = name
    dataclass.sort = int(request.GET.get("sort"))
    dataclass.type = int(request.GET.get("type"))
    dataclass.save()

    if id != 0:
        return commons.res_success("更新成功")
    else:
        return commons.res_success("添加成功")

def ajax_dataclass_del(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")
    id = request.GET.get("id")
    try:
        dataclass = DataClass.objects.get(id = id)

        child_count = DataClass.objects.filter(parent_id = dataclass.id).count()
        if child_count > 0 :
            DataClass.deleteById(dataclass.id)
        Data.objects.filter(dataclass_id = dataclass.id).delete()
        dataclass.delete()
        return commons.res_success("删除成功")
    except:
        return commons.res_fail(1, "该数据不存在")

def ajax_data_list(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登陆")
    #分页搜索
    page = 1
    if request.GET.get("page"):
        page = int(request.GET.get("page"))
    page_size = cfg.page_size
    if request.GET.get("page_size"):
        page_size = int(request.GET.get("page_size"))
    type = int(request.GET.get("type"))
    res_data = Data.getList(page, page_size, type)
    return commons.res_success("请求成功", res_data)

def ajax_data_add(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登陆")
    id = 0
    if request.POST.get("id"):
        id = int(request.POST.get("id"))
    name = request.POST.get("name")
    content = request.POST.get("content")

    if not name or name == "":
        return commons.res_fail(1, "名称不能为空")
    elif not content or content == "":
        return commons.res_fail(1, "内容不能为空")

    data = None
    if id != 0:
        data = Data.object.get(id = id)
    else:
        data = Data()
        data.hits = 0
        data.add_time = int(time.time())

    data.name = name
    data.content = content
    data.dataclass_id = int(request.POST.get("dataclass_id"))
    data.sort = int(request.POST.get("sort"))
    data.type = int(request.POST.get("type"))
    data.picture = ""
    data.save()

    if id != 0:
        return commons.res_success("更新成功")
    else:
        return commons.res_success("添加成功")

def ajax_data_get(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")
    try:
        id = request.GET.get("id")
        data = Data.objects.get(id = id)
        return commons.res_success("请求成功", json.loads(data.toJSON()))
    except:
        return commons.res_fail(1, "找不到该数据")

def ajax_data_del(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")
    id = int(request.GET.get("id"))

    try:
        data = Data.objects.get(id = id)
        data.delete()
        return commons.res_success("删除成功")
    except:
        return commons.res_fail(1, "该数据不存在")

def ajax_art_single_get(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登录")

    id = request.GET.get("id")
    obj = ArtSingle.objects.get(id = id)
    return commons.res_success("请求成功", json.loads(obj.toJSON()))

def ajax_art_single_update(request):
    if not request.session.get("sess_admin"):
        return commons.res_fail(1, "需要登陆")
    id = request.GET.get("id")
    content = request.GET.get("content")

    obj = ArtSingle.objects.get(id = id)
    obj.content = content
    obj.save()
    return commons.res_success("更新成功")


