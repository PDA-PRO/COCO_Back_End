from .base import Crudbase
from app.db.base import DBCursor

class CrudHot(Crudbase):
    def hot_list(self,db_cursor:DBCursor):
        board_sql = """
            select b.*, i.user_id from coco.boards as b, coco.boards_ids as i 
            where b.id = i.board_id
            order by likes desc limit 1;
        """
        board_result = db_cursor.select_sql(board_sql)
        if len(board_result) > 0:
             board_result = board_result[0]
             board_data = {
                'board_id': board_result["id"],
                'user_id': board_result["user_id"],
                'time': board_result["time"],
                'category': board_result["category"],
                'views': board_result["views"],
                'comments': board_result["comments"],
                'likes': board_result["likes"],
                'title': board_result["title"],
             }
        else:
            board_data = False
        
        task_sql = """
            select count(*), i.task_id, t.title, t.rate, t.mem_limit, t.time_limit, t.diff 
            from coco.sub_ids as i , coco.task as t
            where i.task_id = t.id group by i.task_id order by count(*) 
            desc limit 1;
        """
        task_result = db_cursor.select_sql(task_sql)
        if len(task_result)>0:
            task_result = task_result[0]
            task_data = {
                'problem_submitCount': task_result["count(*)"], 
                'problem_id': task_result["task_id"],
                'problem_title': task_result["title"],
                'problem_rate': task_result["rate"],
                'problem_memLimit': task_result["mem_limit"],
                'problem_timeLimit': task_result["time_limit"],
                'problem_diff': task_result["diff"]
            }
        else:
            task_data = False
            
        return {
            'board': board_data,
            'problem': task_data
        }
        # return {
        #     'board_id': board_result["id"],
        #     'user_id': board_result["user_id"],
        #     'time': board_result["time"],
        #     'category': board_result["category"],
        #     'views': board_result["views"],
        #     'comments': board_result["comments"],
        #     'likes': board_result["likes"],
        #     'title': board_result["title"],
        #     'problem_submitCount': task_result["count(*)"], 
        #     'problem_id': task_result["task_id"],
        #     'problem_title': task_result["title"],
        #     'problem_rate': task_result["rate"],
        #     'problem_memLimit': task_result["mem_limit"],
        #     'problem_timeLimit': task_result["time_limit"],
        #     'problem_diff': task_result["diff"]
        # }

    def my_status(self, db_cursor:DBCursor,user_id):
        data = user_id
        solved_list_sql = """
            SELECT time, task_id, diff
            FROM coco.user_problem
            WHERE user_id = %s AND status = 3
            GROUP BY task_id, time ORDER BY time DESC;   
        """
        solved_list_result = db_cursor.select_sql(solved_list_sql, data)
        growth = [] #성장 그래프
        for i in range(len(solved_list_result)-1, -1, -1):
            if not growth: #성장 그래프 리스트가 비어있으면
                growth.append([solved_list_result[i]['time'], solved_list_result[i]['diff']])
                #새로운 달에 저장
            else:
                if solved_list_result[i]['time'] == growth[-1][0]: #리스트 마지막 달과 같으면
                    growth[-1][1] += solved_list_result[i]['diff'] #해당 달에 누적
                else: #새로운 달에 그 전까지 누적값 저장
                    growth.append([solved_list_result[i]['time'], growth[-1][1]+solved_list_result[i]['diff']])

        if len(growth) < 8:
            for i in range(len(growth), 8):
                growth.append(['0000', 0])    

        growth.sort(reverse=True)
 
        diff = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        problem_diff_sql = """
            SELECT diff, count(*) as cnt FROM coco.status_all as s, coco.view_task as t
            where s.user_id = %s and s.status = 3 and s.task_id = t.id group by diff;
        """
        problem_diff_result = db_cursor.select_sql(problem_diff_sql, data)


        task_cnt_sql = 'SELECT diff, count(*) as cnt FROM coco.task group by diff order by diff;'
        task_cnt_result = db_cursor.select_sql(task_cnt_sql, ())
        cnt = {}
        for item in task_cnt_result:
            cnt[item['diff']] = item['cnt']

        for i in problem_diff_result:
            diff[i['diff']] = i['cnt'] / cnt[i['diff']]
        
        return {
            'growth': growth,
            'diff': diff
        }

hot_crud=CrudHot()
