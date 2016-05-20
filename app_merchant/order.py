#--coding:utf-8--#
import pymongo
import sys

from app_merchant import auto
from tools import tools
import time
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hcy'
from flask import Blueprint,jsonify,abort,render_template,request,json
from connect import conn
from bson import ObjectId,json_util
import tools.tools as tool
import tools.public_vew as public
import datetime
table = {'status': 'int',
         'type': 'int',
         'restaurant_id': 'obj',
         '_id': 'obj',
         'username':'str',
         'phone':'str',
         'demand':'str',
         'numpeople':'int',
          'preset_time':''
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
        try:
            pdict = {
                'restaurant_id':request.form["restaurant_id"],
                'status':request.form["status"],
                'type':request.form["type"]
            }
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
            item = mongo.order.find(tools.orderformate(pdict, table),second).sort("add_time", pymongo.DESCENDING)[star:end]
            allcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"])}).count()
            newcount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":0}).count()
            waitecount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":2}).count()
            redocount = mongo.order.find({'restaurant_id':ObjectId(request.form["restaurant_id"]),"status":6}).count()
            data=[]
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
                data.append(json)
            data.append({'allcount':allcount,'newcount':newcount,'waitecount':waitecount,'redocount':redocount})

            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,data)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
        except Exception,e:
            print e
            result=tool.return_json(0,"success",False,None)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
         return abort(403)
#1.1.4.jpg订单详细信息form:id
@order_api.route('/fm/merchant/v1/order/orderinfos/', methods=['POST'])
def orderinfos():
    if request.method=='POST':
        pdict = {
            '_id':request.form["id"]
        }
        item = mongo.order.find(tools.orderformate(pdict, table))
        data=[]
        for i in item:
            json = {}
            for key in i.keys():
                if key == '_id':
                    json['id'] = str(i[key])
                elif key == 'restaurant_id':
                    json['restaurant_id'] = str(i[key])
                elif key == 'webuser_id':
                    json['webuser_id'] = str(i[key])
                elif key == 'preset_time':
                    json['preset_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                elif key == 'add_time':
                    json['add_time'] = i[key].strftime('%Y年%m月%d日 %H:%M')
                else:
                    json[key] = i[key]
            data.append(json)

        jwtmsg = auto.decodejwt(request.form["jwtstr"])
        result=tool.return_json(0,"success",jwtmsg,data)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#1.2.jpg订单-统计|restaurant_id:饭店id|start_time:开始时间|end_time：结束时间|
@order_api.route('/fm/merchant/v1/order/ordercounts/', methods=['POST'])
def ordercounts():
    if request.method == 'POST':
        start=datetime.datetime(*time.strptime(request.form['start_time'],'%Y-%m-%d')[:6])
        end = datetime.datetime(*time.strptime(request.form['end_time'],'%Y-%m-%d')[:6])+datetime.timedelta(days = 1)
        pdict = {'restaurant_id':ObjectId(request.form['restaurant_id']),'add_time': {'$gte': start, '$lt': end}}
        allcount = mongo.order.find(pdict).count()
        anumpeoples = mongo.order.aggregate([{ '$match' : pdict}, { '$group' : { '_id' : "$restaurant_id", 'numpeople' : {'$sum' : "$numpeople"} }}])
        json = {}
        for i in anumpeoples:
                for key in i.keys():
                    if key == '_id':
                        json['id'] = str(i[key])
                    else:
                        json[key] = i[key]
        pdict['source'] = 1
        ycount = mongo.order.find(pdict).count()
        pdict['source'] = 2
        mcount = mongo.order.find(pdict).count()
        data={'allcount':allcount,'anumpeoples':json,'ycount':ycount,'mcount':mcount}
        jwtmsg = auto.decodejwt(request.form["jwtstr"])
        result=tool.return_json(0,"success",jwtmsg,data)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#1.3.0.jpg餐位管理restaurant_id, preset_time
@order_api.route('/fm/merchant/v1/order/orderbypreset/', methods=['POST'])
def orderbypreset():
    if request.method=='POST':
        data = public.getroomslist(ObjectId(request.form['restaurant_id']),request.form['preset_time'])
        jwtmsg = auto.decodejwt(request.form["jwtstr"])
        result=tool.return_json(0,"success",jwtmsg,data)
        return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
#1.3.2餐位管理修改订单
@order_api.route('/fm/merchant/v1/members/updateorder/', methods=['POST'])
def updateorder():
    if request.method=='POST':
            pdict = {
                '_id':request.form["id"],
                'username':request.form["username"],
                'phone':request.form["phone"],
                'demand':request.form["demand"],
                'numpeople':request.form["numpeople"],
                'preset_time':request.form["preset_time"]
            }
            mongo.order.update_one({'_id':ObjectId(request.form['id'])},{"$set":tools.orderformate(pdict, table)})
            json = {
                    "status": 1,
                    "msg":""
            }
            jwtmsg = auto.decodejwt(request.form["jwtstr"])
            result=tool.return_json(0,"success",jwtmsg,json)
            return json_util.dumps(result,ensure_ascii=False,indent=2)
    else:
        return abort(403)
