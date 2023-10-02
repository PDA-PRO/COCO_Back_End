from .base import Crudbase
import json

class CrudAlarm(Crudbase):
    def create_alarm(self, db_cursor, info):
        sql, data = '', ''
        # 1: 내 게시글에 댓글, 2: 내 게시글 좋아요, 3: 내 댓글 좋아요
        if info['context'] == 1 or info['context'] == 2 or info['context'] == 3:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('board_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['board_id'], info['category'])
            db_cursor.execute_sql(sql, data)
        # 5: 튜터가 튜티 스룸에 초대
        if info['context'] == 5:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'],info['context']['room_id'],info['context']['room_name'], info['category'])
            db_cursor.execute_sql(sql, data) 
        # 6: 스룸 삭제
        if info['context'] == 6:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_name'], info['category'])
            db_cursor.execute_sql(sql, data)  
        # 7: 스룸 질문에 답변 남김
        if info['context'] == 7:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'q_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['context']['q_id'], info['category'])
            db_cursor.execute_sql(sql, data) 
        # 8: 스룸 질문에 답변 채택
        if info['context'] == 8:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['category'])
            db_cursor.execute_sql(sql, data)
        # 9: 스룸에 새로운 로드맵, 10: 로드맵 업뎃
        if info['context'] == 9 or info['context'] == 10:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s, 'roadmap_name', %s, 'roadmap_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'],info['context']['room_name'], info['context']['roadmap_name'], info['context']['roadmap_id'], info['category'])
            db_cursor.execute_sql(sql, data)  
        # 11: 스룸에 새로운 질문
        if info['context'] ==11:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['context']['room_name'], info['category'])
            db_cursor.execute_sql(sql, data)            
        return True
    
    def read_alarm(self, db_cursor, user_id):
        sql = '''
            SELECT receiver, sender, is_read, context, time, category 
            FROM coco.alarm where receiver = %s order by time desc;
        '''
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        return result



alarm_crud=CrudAlarm()