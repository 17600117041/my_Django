
from django.db import models
import json
import time
from . import commons

def to_json(obj):
	fields = []
	for field in obj._meta.fields:
		fields.append(field.name)
	d = {}
	for attr in fields:
		val = getattr(obj, attr)
		
		#如果是model类型，就要再一次执行model转json
		if isinstance(val, models.Model):
			val = json.loads(to_json(val))
		d[attr] = val
	return json.dumps(d)

class Admin(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	pwd = models.CharField(max_length = 50)
	add_time = models.IntegerField(default = 0)
	
	def toJSON(self):
		return to_json(self)
	
	#获取分页数据，静态方法
	@staticmethod
	def getList(page, page_size):
		total = Admin.objects.all().count()
		page_count = commons.page_count(total, page_size)
	
		offset = (page - 1) * page_size
		limit = offset + page_size
		admin_list = Admin.objects.all().order_by("-id")[offset:limit]
	
		admin_list_json = []
		for admin in admin_list:		
			item = json.loads(admin.toJSON())
			item["add_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["add_time"]))
			
			#移除密码
			del item["pwd"]
			admin_list_json.append(item)
	
		data = {
			"page_size": page_size,
			"page_count": page_count,
			"total": total,
			"page": page,
			"list": admin_list_json,
		}
		return data

class ArtSingle(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	content = models.TextField()
	
	def toJSON(self):
		return to_json(self)
	
class DataClass(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	parent_id = models.IntegerField(default = 0)
	sort = models.IntegerField(default = 0)
	type = models.IntegerField(default = 0)

	def toJSON(self):
		return to_json(self)
		
	#递归删除分类，静态方法
	@staticmethod
	def deleteById(id):
		dc_list = DataClass.objects.filter(parent_id = id)
	
		for dc in dc_list:
			child_count = DataClass.objects.filter(parent_id = dc.id).count()
			if child_count > 0:
				DataClass.deleteById(dc.id)
		
			#删除该分类下面的对应数据
			Data.objects.filter(dataclass_id = dc.id).delete()
			dc.delete()
			
	#递归获取父分类的dict，静态方法
	@staticmethod
	def getById(id):
		dataclass = DataClass.objects.get(id = id)
		dataclass_json = json.loads(dataclass.toJSON())	
		if dataclass_json["parent_id"] != 0:
			dataclass_json["parent"] = DataClass.getById(dataclass_json["parent_id"])	
		return dataclass_json
		
	#递归获取该分类下的分类(返回list)，静态方法
	@staticmethod
	def listById(id):
		dc_list = DataClass.objects.filter(parent_id = id).order_by("-sort", "-id")
		dc_list_json = []
		for dc in dc_list:
			item = json.loads(dc.toJSON())
				
			child_count = DataClass.objects.filter(parent_id = item["id"]).count()
			if child_count > 0:
				item["children"] = DataClass.listById(item["id"])
			
			dc_list_json.append(item)

		return dc_list_json

class Data(models.Model):
	id = models.AutoField(primary_key = True)
	name = models.CharField(max_length = 50)
	content = models.TextField()
	add_time = models.IntegerField(default = 0)
	dataclass = models.ForeignKey(DataClass)
	sort = models.IntegerField(default = 0)
	type = models.IntegerField(default = 0)
	hits = models.IntegerField(default = 0)
	picture = models.CharField(max_length = 50)

	def toJSON(self):
		return to_json(self)
	
	#获取分页数据，静态方法
	@staticmethod
	def getList(page, page_size, type):
		total = Data.objects.filter(type = type).count()
		page_count = commons.page_count(total, page_size)
	
		offset = (page - 1) * page_size
		limit = offset + page_size
	
		data_list = Data.objects.filter(type = type).order_by("-sort", "-id")[offset:limit]
		data = []
		for i in data_list:
			item = json.loads(i.toJSON())
			item["add_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(item["add_time"]))
			data.append(item)
	
		data = {
			"page_size": page_size,
			"page_count": page_count,
			"total": total,
			"page": page,
			"list": data,
		}
		return data
