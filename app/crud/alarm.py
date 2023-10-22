from .base import Crudbase
import json

class CrudAlarm(Crudbase):
    def create_alarm(self, db_cursor, info):
        print(info)
        sql, data = '', ''
        # 1: 내 게시글에 댓글, 2: 내 게시글 좋아요, 3: 내 댓글 좋아요
        if info['category'] == 1 or info['category'] == 2 or info['category'] == 3:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('board_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['board_id'], info['category'])
        # 5: 튜터가 튜티 스룸에 초대
        if info['category'] == 5:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'],info['context']['room_id'],info['context']['room_name'], info['category'])
        # 6: 스룸 삭제
        if info['category'] == 6:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_name'], info['category'])
        # 7: 스룸 질문에 답변 남김
        if info['category'] == 7:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'q_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['context']['q_id'], info['category'])
        # 8: 스룸 질문에 답변 채택
        if info['category'] == 8:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['category'])
        # 9: 스룸에 새로운 로드맵, 10: 로드맵 업뎃
        if info['category'] == 9 or info['category'] == 10:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s, 'roadmap_name', %s, 'roadmap_id', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'],info['context']['room_name'], info['context']['roadmap_name'], info['context']['roadmap_id'], info['category'])
        # 11: 스룸에 새로운 질문
        if info['category'] ==11:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `sender`, `is_read`, `context`, `time`, `category`) 
                VALUES (%s, %s, '0', json_object('room_id', %s, 'room_name', %s), now(), %s);
            '''
            data = (info['receiver'], info['sender'], info['context']['room_id'], info['context']['room_name'], info['category'])
        # 13: 관리자 권한 획득, 14: 튜터 권한 획득
        if info['category'] == 13 or info['category'] == 4:
            sql = '''
                INSERT INTO `coco`.`alarm` (`receiver`, `is_read`, `time`, `category`) 
                VALUES (%s, '0', now(), %s);
            '''
            data = (info['receiver'], info['category'])
        db_cursor.execute_sql(sql, data) 
        return True
    
    def get_alarm(self, db_cursor, user_id):
        sql = '''
            SELECT receiver, sender, is_read, context, time, category 
            FROM coco.alarm where receiver = %s order by time desc;
        '''
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        return result
    
    def read_alarm(self, db_cursor, user_id):
        sql = 'SELECT id FROM coco.alarm where receiver = %s and is_read = 0;'
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        print(result)
        return result
    
    def check_alarm(self, db_cursor, user_id):
        sql = 'SELECT id FROM coco.alarm where receiver = %s and is_read = 0;'
        data = (user_id)
        result = db_cursor.select_sql(sql, data)
        for item in result:
            sql = 'UPDATE `coco`.`alarm` SET `is_read` = 1 WHERE (`id` = %s);'
            data = (item['id'])
            db_cursor.execute_sql(sql, data)
        return True



alarm_crud=CrudAlarm()