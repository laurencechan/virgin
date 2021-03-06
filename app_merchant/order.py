#--coding:utf-8--#
import random
import pymongo

from app_merchant import auto
from tools import tools
import time
import sys
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public

from tools.swagger import swagger
from flasgger import swag_from

import datetime
table = {'status': 'int',
         'type': 'int',
         'restaurant_id': 'obj',
         '_id': 'obj',
         'username':'str',
         'phone':'str',
         'demand':'str',
         'numpeople':'int',
          'preset_time':'',
         'room_id':'str',
         'source':'int'
      }
mongo=conn.mongo_conn()

order_api = Blueprint('order_api', __name__, template_folder='templates')

@order_api.route('/fm/merchant/v1/order/addorder/',methods=['POST'])
def addorder():
    if request.method == 'POST':
        username=request.form['username']
        phone=request.form['phone']
        numpeople=request.form['numpeople']
        is_room=request.form['is_room']
        preset_time=request.form['preset_time']
        demand=request.form['demand']
        preset_dishs=request.form['preset_dishs']
        source=request.form['source']
        if request.form['deposit']=="":
            deposit = 0
        else:
            deposit=request.form['deposit']
        type = request.form['type']
        restaurant_id=request.form['restaurant_id']
        room_id=request.form['room_id']
        webuser_id=request.form['webuser_id']
        dis_message=request.form['dis_message']
        preset_dishs=[]
    json = {
        "username": username, #1
        "phone": phone,#1
        "numpeople": int(numpeople),#1
        "is_room": bool(is_room),#1
        "preset_time":  preset_time,#1
        "add_time":datetime.datetime.now(),#1
        "demand": demand,#1
        "status": 0,#1
        "source": int(source),#1
        "restaurant_id": ObjectId(restaurant_id),#1
        "room_id": room_id,
        "webuser_id": ObjectId(webuser_id),#1
        "deposit": float(deposit),
        "dis_message": dis_message,#1
        "type": int(type),#1
        "preset_dishs":preset_dishs#1
    }
    mongo.order.insert_one(json)
    jwtmsg = auto.decodejwt(request.form["jwtstr"])
    result=tool.return_json(0,"success",jwtmsg,json_util.dumps(json))
    return result




@order_api.route('/fm/merchant/v1/order/onedishsorder/<string:order_id>/<int:order_type>/', methods=['GET'])
def onedishsorder(order_id,order_type):
    item = mongo.order.find_one({"_id":ObjectId(order_id)})
    item = json_util.loads(json_util.dumps(item))
    if order_type==0:#��λ����
        json = {
            "demand":item["demand"],
            "roomlist":list(public.getroomslist(str(item["restaurant_id"])))
        }
    else:#��Ʒ����
        amount=0.0
        for i in item["preset_dishs"]:
            if i["discount_price"]=="":
                amount+=i["price"]
            else:
                amount+=float(i["discount_price"])
        json= {
            "demand":item["demand"],
            "dis_message":item["dis_message"],
            "amount":amount,
            "roomlist":public.getroomslist(str(item["_id"]))
        }
    jwtmsg = auto.decodejwt(request.form["jwtstr"])
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)




@order_api.route('/fm/merchant/v1/order/dispose/', methods=['POST'])
def dispose():
    if request.method == "POST":
        jwtstr = request.form["jwtstr"]
        order_id = request.form["order_id"]
    item = mongo.order.find_one({"_id":ObjectId(order_id)})
    item = json_util.loads(json_util.dumps(item))
    json = {
            "username": item["username"],
            "phone": item["phone"],
            "numpeople": int(item["numpeople"]),
            "is_room": bool(item["is_room"]),
            "preset_time":  item["preset_time"].strftime('%Y年%m月%d日 %H:%M'),
            "demand": item["demand"],
            "preset_dishs":item["preset_dishs"]
        }
    jwtmsg = auto.decodejwt(jwtstr)
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)






@order_api.route('/fm/merchant/v1/order/accept/<string:order_id>/', methods=['PUT'])
def accept(order_id):
    room_id = request.form["room_id"]
    deposit = request.form["deposit"]  # 订金：之后需要根据指定规则进行修改
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"room_id":room_id,"deposit":deposit,"status":1}})
    json = {
            "order_id": item,
            "status": 1,
            "msg":""
    }
    jwtmsg = auto.decodejwt(request.form["jwtstr"])
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)




@order_api.route('/fm/merchant/v1/order/decline/<string:order_id>/', methods=['PUT'])
def decline(order_id):
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"status":2}})
    json = {
            "order_id": item,
            "status": 2,
            "msg":""
    }
    jwtmsg = auto.decodejwt(request.form["jwtstr"])
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)


@order_api.route('/fm/merchant/v1/order/notification/<string:order_id>/', methods=['PUT'])
def notification(order_id):
    item = mongo.order.update_one({"_id":ObjectId(order_id)},{"$set":{"status":2}})
    json = {
            "order_id": item,
            "status": 2,
            "msg":""
    }
    jwtmsg = auto.decodejwt(request.form["jwtstr"])
    result=tool.return_json(0,"success",jwtmsg,json)
    return json_util.dumps(result,ensure_ascii=False,indent=2)
#1.1.3.jpg全部订单和1.v1.jpg订单restaurant_id,status,type
@order_api.route('/fm/merchant/v1/order/allorder/', methods=['POST'])
def allorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:

                pdict = {
                    'restaurant_id':ObjectId(request.form["restaurant_id"]),
                    'source':2
                }
                if int(request.form["status"]) not in [-1,8]:
                    pdict['status'] = int(request.form["status"])
                if int(request.form["type"]) != -1:
                    pdict['type'] = int(request.form["type"])
                second = {
                    "_id" : 1,
                    "username" :1,
                    "status" : 1,
                    "type" : 1,
                    "restaurant_id" : 1,
                    "numpeople" : 1,
                    "preset_time" : 1,
                    "add_time" : 1
                }
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                # print tools.orderformate(pdict, table)
                item = mongo.order.find(pdict,second).sort("add_time", pymongo.DESCENDING)[star:end]
                # allcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),'source':2}).count()
                newcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":0,'source':2}).count()
                waitecount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":2,'source':2}).count()
                redocount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":6,'source':2}).count()
                allcount = int(newcount)+int(waitecount)+int(redocount)
                data = {}
                list=[]
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                        elif key == 'preset_time':
                            json['preset_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        else:
                            json[key] = i[key]
                    list.append(json)
                data['list'] = list
                data['count'] = {'allcount':allcount,'newcount':newcount,'waitecount':waitecount,'redocount':redocount}
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
#1.1.0.jpg全部订单restaurant_id,status,type
@order_api.route('/fm/merchant/v1/order/newallorder/', methods=['POST'])
def newallorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:

                pdict = {
                    'restaurant_id':ObjectId(request.form["restaurant_id"]),
                    'source':2
                }
                if int(request.form["status"]) != -1 and int(request.form["status"])!=8:
                    if int(request.form["status"]) == 6:
                        pdict['add_time'] = {'$gte': datetime.datetime.now()-datetime.timedelta(days = 30), '$lt': datetime.datetime.now()}
                        pdict['status'] = int(request.form["status"])
                    else:
                        pdict['status'] = int(request.form["status"])
                if int(request.form["type"]) != -1:
                    pdict['type'] = int(request.form["type"])
                second = {
                    "_id" : 1,
                    "username" :1,
                    "status" : 1,
                    "type" : 1,
                    "restaurant_id" : 1,
                    "numpeople" : 1,
                    "preset_time" : 1,
                    "add_time" : 1
                }
                pageindex = request.form["pageindex"]
                pagenum = 10
                star = (int(pageindex)-1)*pagenum
                end = (pagenum*int(pageindex))
                # print tools.orderformate(pdict, table)
                item = mongo.order.find(pdict,second).sort("add_time", pymongo.DESCENDING)[star:end]
                # allcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),'source':2}).count()
                newcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":0,'source':2}).count()
                waitecount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":2,'source':2}).count()
                redocount = mongo.order.find({'add_time':{'$gte': datetime.datetime.now()-datetime.timedelta(days = 30), '$lt': datetime.datetime.now()},'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":6,'source':2}).count()
                allcount = int(newcount)+int(waitecount)+int(redocount)
                data = {}
                list=[]
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                        elif key == 'preset_time':
                            json['preset_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        else:
                            json[key] = i[key]
                    list.append(json)
                data['list'] = list
                data['count'] = {'allcount':allcount,'newcount':newcount,'waitecount':waitecount,'redocount':redocount}
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
#1.1.4.jpg订单详细信息form:id
@order_api.route('/fm/merchant/v1/order/orderinfos/', methods=['POST'])
def orderinfos():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    '_id':request.form["id"]
                }
                item = mongo.order.find(tools.orderformate(pdict, table))
                for i in item:
                    json = {}
                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                            ritem = mongo.restaurant.find({"_id":ObjectId(i[key])},{"dishes_discount":1})
                            for r in ritem:
                                json['discount'] = str(r['dishes_discount']['discount'])
                        elif key == 'webuser_id':
                            json['webuser_id'] = str(i[key])
                        elif key == 'preset_time':
                            json['preset_time'] = i[key].strftime('%Y年%m月%d日 %H:%M:%S')
                        elif key == 'add_time':
                            json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M:%S')
                        elif key == 'room_id':
                            item = mongo.restaurant.find({"_id":ObjectId(i['restaurant_id'])},{"rooms":1})
                            json['rname'] = ''
                            for t in item:
                                for r in t['rooms']:
                                    if r['room_id'] == i['room_id']:
                                        json['rname'] = r['room_name']
                        elif key == 'webuser_id':
                            json['webuser_id'] = str(i[key])
                        elif key == 'total':
                            json['total'] = str(i[key])

                        elif key == 'deposit':
                            if float(i['total']) - float(i['deposit'])<0:
                                json['deposit'] =0
                            else:
                                json['deposit'] = str('%.2f' % (float('%.2f' % (float(i['total']) - float(i['deposit']))) * 0.1))
                        elif key == 'preset_dishs':
                            pdlist = []

                            if i[key]!=None:
                                for pd in i[key]:
                                    pdjson = {}
                                    pdjson['id'] = pd['id']
                                    pdjson['price'] = str(pd['price'])
                                    pdjson['num'] = pd['num']
                                    pdjson['name'] = pd['name']
                                    pdjson['discount_price'] = str(pd['discount_price'])
                                    pdlist.append(pdjson)
                            json['preset_dishs'] = pdlist
                        elif key == 'preset_wine':
                            pdlist = []

                            if i[key]!=None:
                                for pd in i[key]:
                                    pdjson = {}
                                    pdjson['id'] = pd['id']
                                    pdjson['price'] = str(pd['price'])
                                    pdjson['num'] = pd['num']
                                    pdjson['name'] = pd['name']
                                    pdjson['discount_price'] = str(pd['discount_price'])
                                    pdlist.append(pdjson)
                            json['preset_wine'] = pdlist
                        else:
                            json[key] = i[key]

                result=tool.return_json(0,"success",True,json)
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

#iOS 用 1.2.jpg订单-统计
@order_api.route('/fm/merchant/v1/order/ordercounts1/', methods=['POST'])
def ordercounts1():
    if request.method == 'POST':
        type = request.form["type"] #1- 定座统计   2-消费统计
        if auto.decodejwt(request.form['jwtstr']):
            # try:
                start=datetime.datetime(*time.strptime(request.form['start_time'],'%Y-%m-%d')[:6])
                end = datetime.datetime(*time.strptime(request.form['end_time'],'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
                data= {
                        "aytotal": 0.0,
                        "amtotal": 0.0,
                        "watotal": 0.0,
                        "yatotal": 0.0,
                        "wmtotal": 0.0,
                        "ymtotal": 0.0,
                        "yytotal": 0.0,
                        "wytotal": 0.0,
                        "atotal":  0.0,
                        "mnumpeople": 0,
                        "anumpeople": 0,
                        "ycount": 0.0,
                        "yanumpeople": 0,
                        "allcount": 0.0,
                        "mcount": 0.0
                      }
                pdict = {'status':{'$in': [0,1, 2, 3, 4, 5, 6, 7]},'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                ndict = { '$group' : { '_id' : "$restaurant_id", 'numpeople': {'$sum': "$numpeople"} }}
                allcount = mongo.order.find(pdict).count()
                anumpeoples = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                data['allcount'] = allcount
                for i in anumpeoples:
                    data['anumpeople'] = i['numpeople']
                pdict['source'] = 1
                ycount = mongo.order.find(pdict).count()
                yanumpeople = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                data['ycount'] = ycount
                for i in yanumpeople:
                    data['yanumpeople'] = i['numpeople']
                pdict['source'] = 2
                mcount = mongo.order.find(pdict).count()
                data['mcount'] = mcount
                mnumpeople = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                for i in mnumpeople:
                    data['mnumpeople'] = i['numpeople']
                gdict = { '$group' : { '_id' : "$restaurant_id", 'total': {'$sum': "$total"} }}
                pdict['status'] = {'$in': [0,1, 2, 3, 4]}
                atotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in atotal:
                    data['atotal'] = a['total']
                pdict['source'] = 1
                aytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in aytotal:
                    data['aytotal'] = a['total']
                pdict['source'] = 2
                amtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                total2 = 0.0
                for a in amtotal:
                    total2 = a['total']
                    data['amtotal'] = a['total']
                pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                pdict['status'] = {'$in': [0,1, 2, 3]}

                watotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in watotal:
                    data['watotal'] = a['total']
                pdict['source'] = 1
                wytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in wytotal:
                    data['wytotal'] = a['total']
                pdict['source'] = 2
                wmtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in wmtotal:
                    data['wmtotal'] = a['total']
                pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                pdict['status'] = 4
                yatotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in yatotal:
                    data['yatotal'] = a['total']
                pdict['source'] = 1
                yytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in yytotal:
                    data['yytotal'] = a['total']
                pdict['source'] = 2
                ymtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in ymtotal:
                    print a
                    data['ymtotal'] = a['total']
                if int(type)==1:
                    content="<p style=\"margin-left: 20px;\">共接收座位预定订单&nbsp;<span style=\"color:red\">"+str(data['allcount'])+"</span>&nbsp;桌，就餐人数&nbsp;<span style=\"color:red\">"+str(data['anumpeople'])+"</span>&nbsp;人；</p><p style=\"margin-left: 20px;\">美食地图预定&nbsp;<span style=\"color:red\">"+str(data['mcount'])+"</span>&nbsp;桌，就餐人数&nbsp;<span style=\"color:red\">"+str(data['mnumpeople'])+"</span>&nbsp;人；</p><p style=\"margin-left: 20px;\">其它方式预定&nbsp;<span style=\"color:red\">"+str(data['ycount'])+"</span>&nbsp;桌，就餐人数&nbsp;<span style=\"color:red\">"+str(data['yanumpeople'])+"</span>&nbsp;人。</p>"

                else:
                    content = "<p style=\"margin-left: 20px;\">共消费"+str(total2)+"</p>"
                json={
                    "content":content
                }
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            # except Exception,e:
            #     print e
            #     return render_template("/test/count.html",allcount = data['allcount'] , anumpeople = data['anumpeople'] , mcount = data['mcount'] , mnumpeople = data['mnumpeople'] , ycount = data['ycount'] , yanumpeople = data['yanumpeople'])





#1.2.jpg订单-统计|restaurant_id:饭店id|start_time:开始时间|end_time：结束时间|
@order_api.route('/fm/merchant/v1/order/ordercounts/', methods=['POST'])
def ordercounts():
    if request.method == 'POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                start=datetime.datetime(*time.strptime(request.form['start_time'],'%Y-%m-%d')[:6])
                end = datetime.datetime(*time.strptime(request.form['end_time'],'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
                data= {
                        "aytotal": 0.0,
                        "amtotal": 0.0,
                        "watotal": 0.0,
                        "yatotal": 0.0,
                        "wmtotal": 0.0,
                        "ymtotal": 0.0,
                        "yytotal": 0.0,
                        "wytotal": 0.0,
                        "atotal":  0.0,
                        "mnumpeople": 0,
                        "anumpeople": 0,
                        "ycount": 0.0,
                        "yanumpeople": 0,
                        "allcount": 0.0,
                        "mcount": 0.0
                      }
                pdict = {'status':{'$in': [0,1, 2, 3, 4, 5, 6, 7]},'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                ndict = { '$group' : { '_id' : "$restaurant_id", 'numpeople': {'$sum': "$numpeople"} }}
                allcount = mongo.order.find(pdict).count()
                anumpeoples = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                data['allcount'] = allcount
                for i in anumpeoples:
                    data['anumpeople'] = i['numpeople']
                pdict['source'] = 1
                ycount = mongo.order.find(pdict).count()
                yanumpeople = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                data['ycount'] = ycount
                for i in yanumpeople:
                    data['yanumpeople'] = i['numpeople']
                pdict['source'] = 2
                mcount = mongo.order.find(pdict).count()
                data['mcount'] = mcount
                mnumpeople = mongo.order.aggregate([{ '$match' : pdict}, ndict])
                for i in mnumpeople:
                    data['mnumpeople'] = i['numpeople']
                gdict = { '$group' : { '_id' : "$restaurant_id", 'total': {'$sum': "$total"} }}
                pdict['status'] = {'$in': [0,1, 2, 3, 4]}
                atotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in atotal:
                    data['atotal'] = round(float(a['total']),2)
                pdict['source'] = 1
                aytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in aytotal:
                    data['aytotal'] = round(float(a['total']),2)
                pdict['source'] = 2
                amtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in amtotal:
                    print a,'11111111111111111111'
                    data['amtotal'] = round(float(a['total']),2)
                pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                pdict['status'] = {'$in': [0,1, 2, 3]}

                watotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in watotal:
                    data['watotal'] = round(float(a['total']),2)
                pdict['source'] = 1
                wytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in wytotal:
                    data['wytotal'] = round(float(a['total']),2)
                pdict['source'] = 2
                wmtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in wmtotal:
                    data['wmtotal'] = round(float(a['total']),2)
                pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
                pdict['status'] = 4
                yatotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in yatotal:
                    data['yatotal'] = round(float(a['total']),2)
                pdict['source'] = 1
                yytotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in yytotal:
                    data['yytotal'] = round(float(a['total']),2)
                pdict['source'] = 2
                ymtotal = mongo.order.aggregate([{ '$match' : pdict}, gdict])
                for a in ymtotal:
                    print a
                    data['ymtotal'] = round(float(a['total']),2)
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




# def ordercounts():
#     if request.method == 'POST':
#         try:
#             start=datetime.datetime(*time.strptime(request.form['start_time'],'%Y-%m-%d')[:6])
#             end = datetime.datetime(*time.strptime(request.form['end_time'],'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
#             pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
#             allcount = mongo.order.find(pdict).count()
#             anumpeoples = mongo.order.aggregate([{ '$match' : pdict}, { '$group' : { '_id' : "$restaurant_id", 'numpeople' : {'$sum' : "$numpeople"} }}])
#             json = {}
#             for i in anumpeoples:
#                     for key in i.keys():
#                         if key == '_id':
#                             json['id'] = str(i[key])
#                         else:
#                             json[key] = i[key]
#             pdict['source'] = 1
#             ycount = mongo.order.find(pdict).count()
#             pdict['source'] = 2
#             mcount = mongo.order.find(pdict).count()
#             data={'allcount':allcount,'anumpeoples':json,'ycount':ycount,'mcount':mcount}
#             jwtmsg = auto.decodejwt(request.form["jwtstr"])
#             result=tool.return_json(0,"success",jwtmsg,data)
#             return json_util.dumps(result,ensure_ascii=False,indent=2)
#         except Exception,e:
#             print e
#             result=tool.return_json(0,"field",False,None)
#             return json_util.dumps(result,ensure_ascii=False,indent=2)
#     else:
#         return abort(403)





#1.3.0.jpg餐位管理restaurant_id, preset_time
# orderbypreset = swagger("订单","餐位管理")
# orderbypreset.add_parameter(name='restaurant_id',parametertype='formData',type='string',required=True,description='饭店id',default='57329b1f0c1d9b2f4c85f8e3')
# orderbypreset.add_parameter(name='preset_time',parametertype='formData',type='string',required= True,description='预定时间',default='2015-6-16')
# orderbypreset.add_parameter(name='jwtstr',parametertype='formData',type='string',required= True,description='jwt串',default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJiYW9taW5nIjoiY29tLnhtdC5jYXRlbWFwc2hvcCIsImlkZW50IjoiOUM3MzgxMzIzOEFERjcwOEY3MkI3QzE3RDFEMDYzNDlFNjlENUQ2NiIsInR5cGUiOiIxIn0.pVbbQ5qxDbCFHQgJA_0_rDMxmzQZaTlmqsTjjWawMPs')
# rjson={
#   "auto": orderbypreset.String(description='验证是否成功'),
#   "code": orderbypreset.Integer(description='',default=0),
#   "date": {
#     "list": [
#       {
#         "room_count": [
#           {
#             "orderinfo": [
#               {
#                 "id": orderbypreset.String(description='',default="572ff4f6ed222e1e28b56056"),
#                 "numpeople": orderbypreset.Integer(description='',default=8),
#                 "preset_time": orderbypreset.String(description='',default="10:10 | 解释"),
#               }
#             ],
#             "room_id": orderbypreset.String(description='',default="201605111054507163"),
#             "room_name": orderbypreset.String(description='',default="中包(1间)"),
#           }
#         ],
#         "room_people_num": orderbypreset.String(description='',default="10-12人包房"),
#       }
#     ]
#   },
#   "message": orderbypreset.String(description='',default="")
# }
@order_api.route('/fm/merchant/v1/order/orderbypreset/', methods=['POST'])
# @swag_from(orderbypreset.mylpath(schemaid='orderbypreset',result=rjson))
def orderbypreset():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                data = public.getroomslist(ObjectId(request.form['restaurant_id']),request.form['preset_time'])
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

#1.3.2餐位管理修改订单
@order_api.route('/fm/merchant/v1/members/updateorder/', methods=['POST'])
def updateorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    'username':request.form["username"],
                    'phone':request.form["phone"],
                    'demand':request.form["demand"],
                    'numpeople':request.form["numpeople"],
                    'room_id':request.form["room_id"],
                    'preset_time':datetime.datetime.strptime(request.form["preset_time"], "%Y-%m-%d %H:%M:%S")
                }
                mongo.order.update_one({'_id':ObjectId(request.form['id'])},{"$set":tools.orderformate(pdict, table)})
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                order = mongo.order.find({"_id":ObjectId(request.form['id'])})
                r_id = ''
                user_id = ''
                for o in order:
                    r_id = o['restaurant_id']
                    user_id = o['webuser_id']
                flag = request.form.get('flag','')
                if user_id !='' and flag != '1':
                    item = tool.tuisong(mfrom=str(r_id),
                             mto=str(user_id),
                             title='您的餐位预订已修改',
                             info='快去看看吧',
                             goto='19',
                             channel='商家拒单',
                             type='1',
                             totype='1',
                             appname='foodmap_user',
                             msgtype='notice',
                             target='device',
                             ext='{"goto":"19","id":"'+request.form['id']+'"}',
                             ispush=True)
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"success",True,json)
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

#1.1.2修改订单状态
@order_api.route('/fm/merchant/v1/members/updatestatus/', methods=['POST'])
def updatestatus():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):
            try:
                mongo.order.update_one({'_id':ObjectId(request.form['order_id'])},{"$set":{"status":int(request.form["status"])}})
#mfrom-消息来源id|mto-发送给谁id数组，下划线分隔|title-消息标题|info-消息内容|goto（"0"）-跳转页位置|channel（订单）-调用位置|type-0系统发 1商家发 2用户发|totype-0发给商家 1发给用户
# appname（foodmap_user，foodmap_shop）-调用的APP|msgtype（message，notice）-是消息还是通知|target（all，device）-全推或单推|ispush（True，False）-是否发送推送|
                if request.form['status'] == '7':
                    rest = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                    phone = ''
                    r_name = ''
                    for r in rest:
                        phone = r['phone']
                        r_name = r['name']
                    order = mongo.order.find({"_id":ObjectId(request.form['order_id'])})
                    addtime = ''
                    for o in order:
                        addtime = o['addtime']
                    item = tool.tuisong(mfrom=request.form['restaurant_id'],
                                 mto=request.form['webuserids'],
                                 title='您的餐位预订已取消',
                                 info='您原定在'+addtime+r_name+'用餐，现在您预定的餐位已经取消，如有疑问请拨打商家电话：'+phone,
                                 goto='17',
                                 channel='商家退单',
                                 type='1',
                                 totype='1',
                                 appname='foodmap_user',
                                 msgtype='notice',
                                 target='device',
                                 ext='{"goto":"11","id":"'+request.form['order_id']+'"}',
                                 ispush=True)
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"success",True,json)
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
#添加订单
@order_api.route('/fm/merchant/v1/order/insertorder/', methods=['POST'])
def insertorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    "order_id":"MSDT%s%03d" % (int(time.time() * 1000), random.randint(1, 999)),
                    "username" : request.form["username"],
                    "is_room":True,
                    "status" : 3,
                    "type" : int(request.form['type']),
                    "source":1,
                    "restaurant_id" : ObjectId(request.form['restaurant_id']),
                    "preset_dishs" : [],
                    "preset_wine": [],
                    "webuser_id" : "",
                    "phone" : request.form['phone'],
                    "dis_message" : "",
                    "room_id" : request.form['room_id'],
                    "deposit" : 0.0,
                    "demand" : request.form['demand'],
                    "total" : 0.0,
                    "numpeople" : int(request.form['numpeople']),
                    "preset_time" : datetime.datetime.strptime(request.form["preset_time"], "%Y-%m-%d %H:%M:%S"),
                    "add_time" : datetime.datetime.now()
                }
                item = mongo.restaurant.find({"rooms.room_id":request.form['room_id']},{"rooms":1})
                for i in item:
                    for room in i['rooms']:
                        if room['room_id'] == request.form['room_id']:
                            if room['room_people_name'] == '大厅':
                                pdict['is_room'] = False
                            else:
                                pdict['is_room'] = True
                        else:
                            pdict['is_room'] = False
                mongo.order.insert(pdict)
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"success",True,json)
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



#添加订单---添加测试数据用
@order_api.route('/fm/merchant/v1/order/insertordertest/', methods=['POST'])
def insertordertest():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            # try:
                type = request.form['type']
                orderdishs=[]

                # rent = mongo.restaurant.find({"_id":ObjectId(request.form['restaurant_id'])})
                # dishs = tools.getdishsitem(str(request.form['restaurant_id']))
                # l=[]
                # b = random.randint(0,len(dishs))
                # for i in range(b):
                #     x=random.randint(0,len(dishs))
                #     if x in l:
                #         continue #这样你就不会选到想同的数了！
                #     else:
                #         l.append(x)
                # for a in l:
                orderdishs=tools.ceshi(str(request.form['restaurant_id']))
                # print orderdishs
                if int(type)==1 and len(orderdishs)>=0:#点菜订单
                    type = 1
                else:
                    orderdishs=[]
                    type = 0
                pdict = {
                    "username" : request.form["username"],
                    "status" : 0,
                    "type" : request.form['type'],
                    "restaurant_id" : ObjectId(request.form['restaurant_id']),
                    "preset_dishs" : orderdishs,
                    "webuser_id" : "",
                    "phone" : request.form['phone'],
                    "dis_message" : "",
                    "room_id" : request.form['room_id'],
                    "deposit" : 0.0,
                    "demand" : request.form['demand'],
                    "total" : 0.0,
                    "numpeople" : request.form['numpeople'],
                    "preset_time" : datetime.datetime.strptime(request.form["preset_time"], "%Y-%m-%d %H:%M:%S"),
                    "add_time" : datetime.datetime.now()
                }
                if request.form['is_room'] == 'true':
                    pdict['is_room'] = True
                else:
                    pdict['is_room'] = False
                mongo.order.insert(pdict)
                json = {
                        "status": 1,
                        "msg":""
                }
                result=tool.return_json(0,"success",True,json)
                return json_util.dumps(result,ensure_ascii=False,indent=2)
            # except Exception,e:
            #     print e
            #     result=tool.return_json(0,"field",False,None)
            #     return json_util.dumps(result,ensure_ascii=False,indent=2)
        else:
            result=tool.return_json(0,"field",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)






#订座和订菜查询```
@order_api.route('/fm/merchant/v1/order/dishroomorder/', methods=['POST'])
def dishroomorder():
    if request.method=='POST':
        if auto.decodejwt(request.form['jwtstr']):

            try:
                pdict = {
                    '_id':request.form["id"]
                }
                item = mongo.order.find(tools.orderformate(pdict, table))
                json = {}
                for i in item:

                    for key in i.keys():
                        if key == '_id':
                            json['id'] = str(i[key])
                        elif key == 'total':
                            json['total'] = str(i[key])
                        elif key == 'demand':
                            json['demand'] = i[key]
                        elif key == 'dis_message':
                            json['dis_message'] = i[key]
                        elif key == 'preset_time':
                            json['preset_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                        elif key == 'restaurant_id':
                            json['restaurant_id'] = str(i[key])
                            json['roomlist'] = public.getroomslist(i[key],i['preset_time'].strftime("%Y-%m-%d"))['list']
                        else:
                            pass

                result=tool.return_json(0,"success",True,json)
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
