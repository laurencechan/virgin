#--coding:utf-8--#
import random

import pymongo
from flasgger import swag_from

from app_merchant import auto
from tools import tools

import sys

from tools.db_app_user import guess
from tools.swagger import swagger

reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime

mongo=conn.mongo_conn()

restaurant_user_api = Blueprint('restaurant_user_api', __name__, template_folder='templates')





restaurant = swagger("饭店","查询类别标签")
restaurant_json = {
    "auto": restaurant.String(description='验证是否成功'),
    "message": restaurant.String(description='SUCCESS/FIELD',default="SUCCESS"),
    "code": restaurant.Integer(description='',default=0),
    "data": {
        "list": [
              {
                "distance": restaurant.String(description='距离，单位是米',default="1983"),
                "wine_discount": restaurant.String(description='酒水优惠',default=""),
                "kind3": restaurant.String(description='店粉抢优惠',default=""),
                "name": restaurant.String(description='饭店名',default="星晨烧烤"),
                "kind1": restaurant.String(description='店粉关注即享',default=""),
                "address": restaurant.String(description='地址',default="哈尔滨市南岗区平公街7-5号"),
                "id": restaurant.String(description='饭店id',default="573542780c1d9b34722f5da9"),
                "guide_image": restaurant.String(description='图片',default="09bb491fcde04edd99e898720c3918df"),
                "district_name": restaurant.String(description='区名',default="南岗区"),
                "business_name": restaurant.String(description='商圈名',default="十字/平公"),
                "restaurant_discount": restaurant.String(description='其他优惠',default=""),
                "dishes_discount": restaurant.String(description='菜品优惠',default=""),
                "kind2": restaurant.String(description='新粉优惠',default="")
              }
        ]
    }
}
restaurant.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant.add_parameter(name='dishes_type',parametertype='formData',type='string',required= True,description='菜系，格式id_id_id',default='10')
restaurant.add_parameter(name='discount',parametertype='formData',type='string',required= True,description='优惠',default='dish')
restaurant.add_parameter(name='room_people_id',parametertype='formData',type='string',required= True,description='包房id',default='40')
restaurant.add_parameter(name='room_type',parametertype='formData',type='string',required= True,description='包房特色，格式id_id_id',default='36')
restaurant.add_parameter(name='tese',parametertype='formData',type='string',required= True,description='特色，格式id_id_id',default='51')
restaurant.add_parameter(name='pay_type',parametertype='formData',type='string',required= True,description='支付，格式id_id_id',default='48')
restaurant.add_parameter(name='pageindex',parametertype='formData',type='string',required= True,description='页数',default='1')
restaurant.add_parameter(name='x',parametertype='formData',type='string',required= True,description='坐标x，没有传x',default='126.62687122442075')
restaurant.add_parameter(name='y',parametertype='formData',type='string',required= True,description='坐标y，没有传y',default='45.764067772341264')
#饭店列表 条件很多
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant/',methods=['POST'])
@swag_from(restaurant.mylpath(schemaid='restaurant',result=restaurant_json))
def restaurant():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pass
                data = {}
# first = {"dishes_type.id":"10","dishes_discount.message":{"$ne":""},"rooms.room_type.id":"36","tese.id":"54","pay_type.id":{"$in":["48"]},"_id":{"$in":[ObjectId("57329e300c1d9b2f4c85f8e6")]}}
                first = {}
                #菜系
                if request.form['dishes_type']!='-1':
                    first["dishes_type.id"] = request.form['dishes_type']
                #饭店优惠
                if request.form['discount']!='-1':
                    if request.form['discount'] == 'dish':
                        first["dishes_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'wine':
                        first["wine_discount.message"] = {"$ne":""}
                    elif request.form['discount'] == 'other':
                        first["restaurant_discount.message"] = {"$ne":""}
                    else:
                        pass
                #包房
                if request.form['room_people_id']!='-1':
                    first["rooms.room_people_id"] = request.form['room_people_id']
                #包房特色
                if request.form['room_type']!='-1':
                    b_idlist = request.form['room_type'].split('_')
                    bidlist = []
                    for mid in b_idlist:
                        if mid != '' and mid != None:
                            bidlist.append(mid)
                    first["rooms.room_type.id"] = {"$in":bidlist}
                #特色
                if request.form['tese']!='-1':
                    t_idlist = request.form['tese'].split('_')
                    tidlist = []
                    for mid in t_idlist:
                        if mid != '' and mid != None:
                            tidlist.append(mid)
                    first["tese.id"] = {"$in":tidlist}
                #支付
                if request.form['pay_type']!='-1':
                    pass
                    idlist = request.form['pay_type'].split('_')
                    midlist = []
                    for mid in idlist:
                        if mid != '' and mid != None:
                            midlist.append(mid)
                    first["pay_type.id"] = {"$in":midlist}
                # #范儿店
                # if request.form['recommend']!='-1':
                #     pass
                #     #
                #     if request.form['recommend_type']!='-1':
                #         item = mongo.shop_recommend.find({"type":1},{"restaurant_id":1})
                #     else:
                #         item = mongo.shop_recommend.find({},{"restaurant_id":1})
                #     r_idlist = []
                #     for i in item:
                #         r_idlist.append(i['restaurant_id'])
                #     first['_id'] = {"$in":r_idlist}
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                list = guess(first=first,lat1=float(request.form['x']),lon1=float(request.form['y']),start=star,end=end)
                data['list'] = list
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#图片展示列表
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_img/',methods=['POST'])
def restaurant_img():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                item = mongo.restaurant.find({'_id':ObjectId(request.form["restaurant_id"])})
                type = request.form['type']
                data ={}
                dishs_list =[]
                photo_list = []
                room_list = []
                for i in item:
                    #菜品图片 开始
                    if type == '1' or type == '-1':
                        for dishs in i['menu']:
                            if dishs['name'] !='优惠菜' and dishs['name'] !='推荐菜' and dishs['dish_type'] =='1' and dishs['dishs']!=[]:
                                for dish in dishs['dishs']:
                                    json = {}
                                    json['name'] = dish['name']
                                    json['guide_image'] = dish['guide_image']
                                    dishs_list.append(json)
                    #菜品图片 结束
                    #环境图片 开始
                    if type == '2' or type == '-1':
                        for photo in i['show_photos']:
                            pjson = {}
                            pjson['img'] = photo['img']
                            pjson['desc'] = photo['desc']
                            photo_list.append(pjson)
                    #环境图片 结束
                    #包房图片 开始
                    if type == '3' or type == '-1':
                        for room in i['rooms']:
                            for room_photo in room['room_photo']:
                                rjson = {}
                                rjson['img'] = room_photo['img']
                                rjson['desc'] = room_photo['desc']
                                room_list.append(rjson)
                    #包房图片 结束
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                dishs_list[0:0] = room_list
                dishs_list[0:0] = photo_list
                data['list'] = dishs_list[star:end]
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",False,None)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#饭店查询类别标签
restaurant_type = swagger("饭店","查询类别标签")
restaurant_type.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
restaurant_type_json = {
  "auto": restaurant_type.String(description='验证是否成功'),
  "code": restaurant_type.Integer(description='',default=0),
  "message": restaurant_type.String(description='SUCCESS/FIELD',default="SUCCESS"),
  "data": {
    "baofang": [
      {
        "id": restaurant_type.String(description='包房id',default="39"),
        "name": restaurant_type.String(description='包房名',default="2-4人包房")
      }
    ],
    "baofangtese": [
      {
        "id": restaurant_type.String(description='包房特色id',default="36"),
        "name": restaurant_type.String(description='包房特色',default="带洗手间包房")
      }
    ],
    "fenlei": [
      {
        "id": restaurant_type.String(description='菜系id',default="2"),
        "name": restaurant_type.String(description='菜系名',default="快餐/小吃")
      }
    ],
    "zhifu": [
      {
        "id": restaurant_type.String(description='支付方式id',default="47"),
        "name": restaurant_type.String(description='支付方式',default="刷卡支付")
      }
    ],
    "tese": [
      {
        "id": restaurant_type.String(description='特色id',default="51"),
        "name": restaurant_type.String(description='特色',default="演艺")
      }
    ],
    "youhui": [
      {
        "id": restaurant_type.String(description='优惠类别',default="dish"),
        "name": restaurant_type.String(description='优惠类别名',default="菜品优惠")
      }
    ]
  },
}
#饭店查询类别标签
@restaurant_user_api.route('/fm/user/v1/restaurant/restaurant_type/',methods=['POST'])
@swag_from(restaurant_type.mylpath(schemaid='restaurant_type',result=restaurant_type_json))
def restaurant_type():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                data = {}
                f_list = []
                b_list = []
                t_list = []
                z_list = []
                bt_list = []
                item = mongo.assortment.find({"parent":{"$in":[1,35,59,50,46]}})
                for i in item:
                    f_json = {}
                    b_json = {}
                    t_json = {}
                    z_json = {}
                    bt_json = {}
                    if i['parent'] == 1:
                        f_json['id'] = str(i['_id'])
                        f_json['name'] = i['name']
                        f_list.append(f_json)
                    elif i['parent'] == 35:
                        b_json['id'] = str(i['_id'])
                        b_json['name'] = i['name']
                        b_list.append(b_json)
                    elif i['parent'] == 59:
                        bt_json['id'] = str(i['_id'])
                        bt_json['name'] = i['name']
                        bt_list.append(bt_json)
                    elif i['parent'] == 50:
                        t_json['id'] = str(i['_id'])
                        t_json['name'] = i['name']
                        t_list.append(t_json)
                    elif i['parent'] == 46:
                        z_json['id'] = str(i['_id'])
                        z_json['name'] = i['name']
                        z_list.append(z_json)
                    else:
                        pass
                data['fenlei'] = f_list
                data['baofang'] = b_list
                data['baofangtese'] = bt_list
                data['tese'] = t_list
                data['zhifu'] = z_list
                data['youhui'] = [{'id':'dish','name':'菜品优惠'},{'id':'wine','name':'酒水优惠'},{'id':'other','name':'其他优惠'}]
                result=tool.return_json(0,"success",True,data)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            except Exception,e:
                print e
                result=tool.return_json(0,"field",True,e)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
