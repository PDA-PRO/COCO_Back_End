import pymysql
import db
from .base import Crudbase

db_server = db.db_server

class CrudHot(Crudbase):
    def hot_list(self):
        board_sql = """
            select b.*, i.user_id from coco.boards as b, coco.boards_ids as i 
            where b.id = i.board_id
            order by likes desc limit 1;
        """
        board_result = self.select_sql(board_sql)
        board_result = board_result[0]
        task_sql = """
            select count(*), i.task_id, t.title, t.rate, t.mem_limit, t.time_limit, t.diff 
            from coco.sub_ids as i , coco.task as t
            where i.task_id = t.id group by i.task_id order by count(*) 
            desc limit 1;
        """
        task_result = self.select_sql(task_sql)
        task_result = task_result[0]
        return {
            'board_id': board_result["id"],
            'user_id': board_result["user_id"],
            'time': board_result["time"],
            'category': board_result["category"],
            'views': board_result["views"],
            'comments': board_result["comments"],
            'likes': board_result["likes"],
            'title': board_result["title"],
            'problem_submitCount': task_result["count(*)"], 
            'problem_id': task_result["task_id"],
            'problem_title': task_result["title"],
            'problem_rate': task_result["rate"],
            'problem_memLimit': task_result["mem_limit"],
            'problem_timeLimit': task_result["time_limit"],
            'problem_diff': task_result["diff"]
        }

hot_crud=CrudHot()
