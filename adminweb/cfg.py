
web_name = "my_django"
jquery = "http://ajax.useso.com/ajax/libs/jquery/2.1.1/jquery.min.js" #jquery2.0以上
page_size = 16

#后台菜单，只支持3级
admin_menu_list = [
	{ 
		"id": 1, 
		"name": "后台管理", 
		"selected": True, 
		"child_menu": [
			{
				"id": 2,
				"name": "数据管理",
				"child_menu": [
					{
						"id": 5,
						"name": "分类列表",
						"url": "dataclass_list.html",
						"param": "type:1", #demo type:1,id:2
					},
					{
						"id": 6,
						"name": "数据列表",
						"url": "data_list.html",
						"param": "type:1",
					},
				]
			},
			{
				"id": 3,
				"name": "区域管理",
				"child_menu": [
					{
						"id": 7,
						"name": "区域管理1",
						"url": "art_single.html",
						"param": "id:1",
					},
				]
			},
			{
				"id": 4,
				"name": "管理员管理",
				"child_menu": [
					{
						"id": 8,
						"name": "修改密码",
						"url": "admin_pwd.html",
					},
					{
						"id": 9,
						"name": "管理员列表",
						"url": "admin_list.html",
					},
				]
			},
		]
	},
	
]
