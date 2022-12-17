import pymysql
import db
import json

db_server = db.db_server

class CrudHot():
    def hot_list(self):
        board_sql = f"""
            select b.*, i.user_id from coco.boards as b, coco.boards_ids as i 
            where b.id = i.board_id
            order by likes desc limit 1;
        """
        board_result = self.execute_mysql(board_sql)[0]
        task_sql = f"""
            select count(*), i.task_id, t.title, t.rate, t.mem_limit, t.time_limit, t.diff 
            from coco.sub_ids as i , coco.task as t
            where i.task_id = t.id group by i.task_id order by count(*) 
            desc limit 1;
        """
        task_result = self.execute_mysql(task_sql)[0]
        return {
            'board_id': board_result[0],
            'user_id': board_result[9],
            'time': board_result[4],
            'category': board_result[5],
            'views': board_result[7],
            'comments': board_result[8],
            'likes': board_result[6],
            'title': board_result[2],
            'problem_id': task_result[1],
            'problem_title': task_result[2],
            'problem_rate': task_result[3],
            'problem_diff': task_result[6],
            'problem_timeLimit': task_result[5],
            'problem_memLimit': task_result[4],
            'problem_submitCount': task_result[0]    
        }

    def execute_mysql(self, query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result
