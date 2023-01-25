from .base import Crudbase

class CrudStatus(Crudbase):
    def select_status(self):
        sql="select * from coco.status_list order by sub_id desc;"
        result = self.select_sql(sql)
        return result

    def select_status_user(self,user_id, lang, result):
        if result:
            if lang == -1:
                sql = """
                    select * from coco.status_list 
                    where user_id = %s and status = 3
                    order by sub_id desc;
                """
                data = (user_id.strip())
            else:
                sql = """
                    select * from coco.status_list 
                    where user_id = %s and lang = %s and status = 3
                    order by sub_id desc;
                """
                data=(user_id.strip(), lang)
        else:
            if lang == -1:
                sql = """
                    select * from coco.status_list 
                    where user_id = %s
                    order by sub_id desc;
                """
                data = (user_id.strip())                
            else:
                sql = """
                    select * from coco.status_list 
                    where user_id = %s and lang = %s
                    order by sub_id desc;
                """
                data=(user_id.strip(), lang)
        result = self.select_sql(sql,data)
        return result

    def status_per_task(self, info):
        #option: 유저별, 언어, 정답
        if info.option[0]:
            if info.option[1] == -1:
                if info.option[2]:
                    #유저별, 문제 검색, 정답
                    sql = """
                        select * from coco.status_list 
                        where user_id = %s and (title like %s or task_id like %s) and status = 3
                        order by sub_id desc;
                    """
                else:
                    #유저별, 문제 검색
                    sql = """
                        select * from coco.status_list 
                        where user_id = %s and (title like %s or task_id like %s)
                        order by sub_id desc;
                    """
                data = (info.user_id, '%'+info.task_info+'%', '%'+info.task_info+'%')
            else:
                if info.option[2]:
                    # 유저별, 문제 검색, 언어별, 정답
                    sql = """
                        select * from coco.status_list 
                        where user_id = %s and (title like %s or task_id like %s) and lang = %s and status = 3
                        order by sub_id desc;
                    """
                else:
                    # 유저별, 문제 검색, 언어별                 
                    sql = """
                        select * from coco.status_list 
                        where user_id = %s and (title like %s or task_id like %s) and lang = %s 
                        order by sub_id desc;
                    """
                data = (info.user_id, '%'+info.task_info+'%', '%'+info.task_info+'%', info.option[1])
        else:
            if info.option[1] == -1:
                if info.option[2]:
                    #문제 검색, 정답
                    sql = """
                        select * from coco.status_list 
                        where (title like %s or task_id like %s) and status = 3
                        order by sub_id desc;
                    """
                else:
                    #문제 검색
                    sql = """
                        select * from coco.status_list 
                        where (title like %s or task_id like %s)
                        order by sub_id desc;
                    """
                data = ('%'+info.task_info+'%', '%'+info.task_info+'%')
            else:
                if info.option[2]:
                    # 문제 검색, 언어별, 정답
                    sql = """
                        select * from coco.status_list 
                        where (title like %s or task_id like %s) and lang = %s and status = 3
                        order by sub_id desc;
                    """
                else:
                    # 문제 검색, 언어별                 
                    sql = """
                        select * from coco.status_list 
                        where (title like %s or task_id like %s) and lang = %s 
                        order by sub_id desc;
                    """
                data = ('%'+info.task_info+'%', '%'+info.task_info+'%', info.option[1])
        result = self.select_sql(sql,data)
        print(result)
        return result

status_crud=CrudStatus()