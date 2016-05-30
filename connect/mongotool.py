# coding=utf-8

from bson import ObjectId, json_util
from flask import json

_author_ = 'dolacmeo'


class MongoAPI:
    __doc__ = """
    Mongo数据库接口:
    插入数据 add   : 直接插入数据
    查找数据 find  : 必须包含'_id'键
    修改数据 fix   : 必须包含'_id'键 修改时需包含{'fix_data': {'key': 'value'}}
    删除数据 remove: 必须包含'_id'键"""

    def __init__(self, conn):
        """初始化需要实例化数据接口
        :type conn: def
        """
        self.conn = conn
        pass

    def add(self, json_data):
        """插入数据: 直接插入字典json_data
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.insert(json_data)
            return {'success': True, '_id': str(json_data['_id'])}
        except Exception, e:
            return {'success': False, 'error': e}

    def find(self, json_data):
        """查找数据: 允许返回多条数据
        :param json_data: :type json_data:dict
        """
        db_data = self.conn.find(json_data)
        return json.loads(json_util.dumps(db_data))

    def find_id(self, json_data):
        """查找数据: 必须包含json_data._id
        :param json_data: :type json_data:dict
        """
        db_data = self.conn.find_one({"_id": ObjectId(json_data['_id'])})
        db_data['_id'] = str(db_data['_id'])
        return json.loads(json_util.dumps(db_data))

    def fix(self, json_data):
        """修改数据: 必须包含json_data._id 修改数据json_data.fix_data
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.update_one({"_id": ObjectId(json_data['_id'])},
                                 {"$set": json_data['fix_data']})
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}

    def remove(self, json_data):
        """删除数据: 必须包含json_data._id
        :param json_data: :type json_data:dict
        """
        try:
            self.conn.remove(json_data)
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}
        pass

    def remove_id(self, _id):
        """删除数据: 必须包含json_data._id
        :param _id: ObjectId :type _id:str
        """
        try:
            self.conn.remove({"_id": ObjectId(_id)})
            return {'success': True}
        except Exception, e:
            return {'success': False, 'error': e}
        pass

    pass

if __name__ == '__main__':
    pass