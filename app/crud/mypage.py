from .base import Crudbase
from core import security
import db

db_server = db.db_server

class CrudMyPage(Crudbase):
    def myinfo(self, user_id):
        sql = "SELECT * FROM coco.user WHERE id = %s;"
        data = user_id
        result = self.select_sql(sql, data)
        return result[0]

    def myproblems(self, user_id):
        data = user_id
        total_submit, total_solved = 1, 1
        #월별 제출수
        submit_cnt_sql = """
            SELECT time, count(*) as cnt FROM coco.user_problem
            where user_id = %s
            GROUP BY time ORDER BY time DESC;     
        """
        submit_cnt_result = self.select_sql(submit_cnt_sql, data)
        submit_cnt = []
        for i in submit_cnt_result:
            total_submit += i['cnt']
            if not submit_cnt:
                submit_cnt.append([i['time'], i['cnt']])
            else:
                if i['time'] == submit_cnt[-1][0]:
                    submit_cnt[-1][1] += i['cnt']
                else:
                    submit_cnt.append([i['time'], i['cnt']])


            
        #월별 맞은 문제 수
        solved_cnt_sql = """
            SELECT time, count(*) as cnt FROM coco.user_problem
            WHERE user_id = %s AND status = '3'
            GROUP BY time ORDER BY time DESC;
        """
        solved_cnt_result = self.select_sql(solved_cnt_sql, data)
        solved_cnt = []
        for i in solved_cnt_result:
            total_solved += i['cnt']
            if not solved_cnt:
                solved_cnt.append([i['time'], i['cnt']])
            else:
                if i['time'] == solved_cnt[-1][0]:
                    solved_cnt[-1][1] += i['cnt']
                else:
                    solved_cnt.append([i['time'], i['cnt']])

        #전체 맞은 문제 리스트 + 성장 그래프
        solved_list_sql = """
            SELECT time, task_id, diff
            FROM coco.user_problem
            WHERE user_id = %s AND status = 3
            GROUP BY task_id, time ORDER BY time DESC;   
        """
        solved_list_result = self.select_sql(solved_list_sql, data)
        solved_list = [] #맞은 문제 리스트
        growth = [] #성장 그래프
        for i in range(len(solved_list_result)-1, -1, -1):
            solved_list.append(solved_list_result[i]['task_id']) # 맞은 문제 저장
            if not growth: #성장 그래프 리스트가 비어있으면
                growth.append([solved_list_result[i]['time'], solved_list_result[i]['diff']])
                #새로운 달에 저장
            else:
                if solved_list_result[i]['time'] == growth[-1][0]: #리스트 마지막 달과 같으면
                    growth[-1][1] += solved_list_result[i]['diff'] #해당 달에 누적
                else: #새로운 달에 그 전까지 누적값 저장
                    growth.append([solved_list_result[i]['time'], growth[-1][1]+solved_list_result[i]['diff']])

        solved_list = sorted(solved_list) #문제 아이디로 정렬

        #전체 푼 문제 리스트
        submit_list_sql = """
            SELECT task_id
            FROM coco.user_problem
            WHERE user_id = %s
            GROUP BY task_id, time ORDER BY time DESC;  
        """
        submit_list_result = self.select_sql(submit_list_sql, data)
        submit_list = []
        for i in range(len(submit_list_result)-1, -1, -1):
            submit_list.append(submit_list_result[i]['task_id'])
        submit_list = sorted(submit_list)
        unsolved_list = set(submit_list) - set(solved_list) 
               

        if len(submit_cnt) < 8:
            for i in range(len(submit_cnt), 8):
                submit_cnt.append(['0000', 0])

        if len(growth) < 8:
            for i in range(len(growth), 8):
                growth.append(['0000', 0])      

        # print('total: ', total_submit, total_solved)
        # print("월별 제출 수: ", submit_cnt)
        # print("월별 정답 수: ", solved_cnt)
        # print("전체 맞은 문제 리스트: ", solved_list)
        # print("성장 그래프: ", sorted(growth, reverse=True))          

        return {
            'month_submit': submit_cnt,
            'month_solved': solved_cnt,
            'solved_list': set(solved_list),
            'unsolved_list': unsolved_list,
            'growth': sorted(growth, reverse=True),
            'rate': round((total_solved/total_submit)*100, 1)
        }

    def myboard(self, user_id):
        sql = "SELECT * FROM coco.view_board WHERE user_id = %s order by time desc;"
        data = user_id
        result = self.select_sql(sql, data)
        return result

    def delete_myboard(self, board_id):
        sql = "delete from coco.comments where id in (select comment_id from coco.comments_ids where board_id = %s);"
        data = board_id
        self.execute_sql(sql, data)

        sql = "delete from coco.boards where id = %s;"
        data = board_id
        self.execute_sql(sql, data)

        boards_cnt = 'SELECT COUNT(*) as cnt FROM coco.boards;'
        boards_reset = "alter table coco.boards auto_increment = 0;"
        self.reset_auto_increment(boards_cnt, boards_reset)

        comments_cnt = 'SELECT COUNT(*) as cnt FROM coco.comments;'
        comments_reset = "alter table coco.comments auto_increment = 0;"
        self.reset_auto_increment(comments_cnt, comments_reset)
        return 1

    def change_pw(self, info):
        sql = "UPDATE coco.user SET pw = %s WHERE id = %s;"
        data = (security.get_password_hash(info.new_info), info.user_id)
        self.execute_sql(sql, data)
        return 1

    def change_email(self, info):
        sql = "UPDATE coco.user SET email = %s WHERE id = %s;"
        data = (info.new_info, info.user_id)
        self.execute_sql(sql, data)
        return 1
    
    def my_task(self, info):
        data = (info.user_id, info.task_id)
        check_sql = "select exists( select 1 from coco.my_tasks where user_id = %s and task_num = %s) as my_task;" 
        result = self.select_sql(check_sql, data)
        check_result = result[0]['my_task']
        if check_result == 0:
            sql ="INSERT INTO `coco`.`my_tasks` (`user_id`, `task_num`) VALUES (%s, %s);"
            self.execute_sql(sql, data)
        else:
            return False
        return True
    
    def task_lists(self, user_id):
        sql = "SELECT task_num FROM coco.my_tasks WHERE user_id = %s;"
        data = (user_id)
        result = self.select_sql(sql, data)
        return result




mypage = CrudMyPage()