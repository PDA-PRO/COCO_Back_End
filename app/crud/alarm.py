from .base import Crudbase
import json

class CrudAlarm(Crudbase):
    def create_alarm(self, db_cursor, info):
        print(info['context'])
        sql = '''
            INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
            VALUES (%s, %s, '0', %s, now(), %s);
        '''
        data = (info['receiver'], info['sender'], '"{}"'.format(info['context']), info['category'])
        db_cursor.execute_sql(sql, data)
        return True
    
    def read_alarm(self, db_cursor, user_id):
        sql = '''
            SELECT receiver, sender, is_read, JSON_UNQUOTE(JSON_EXTRACT(context, "$")) as context, time, category 
            FROM coco.alarm where receiver = %s order by time desc;
        '''
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        return result



alarm_crud=CrudAlarm()