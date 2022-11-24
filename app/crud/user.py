import pymysql
import db
import uuid

db_server = db.db_server

class CrudUser():
    def check_db(user):
        sql = f"SELECT id, pw FROM `coco`.`user` where id = '{user.id}';"
        result = CrudUser.execute_mysql(sql)
        if len(result) == 0:
            return 0
        else:
            if user.pw == result[0][1]:
                return 1
            return 0

    # 새로운 회원 정보 insert
    def insert_db(user):
        sql = f"INSERT INTO `coco`.`user` (`id`, `pw`, `name`, `role`) VALUES ('{user.id}', '{user.pw}', '{user.name}', '{user.role}')"
        CrudUser.insert_mysql(sql)
        if user.role == 0:
            sql = f"INSERT INTO `coco`.`student` (`std_id`, `rate`, `age`, `user_id`) VALUES ('{uuid.uuid1()}', '{0.00}', '{0}', '{user.id}');"
        else:
            sql = f"INSERT INTO `coco`.`teacher` (`tea_id`, `is_manager`, `user_id`) VALUES ('{uuid.uuid1()}', '{0}', '{user.id}');"
        CrudUser.insert_mysql(sql)
        return 1


    # 회원가입시 아이디 중복 검사
    def find_id(id):
        sql = f"SELECT id FROM `coco`.`user` where id = '{id}';"
        result = CrudUser.execute_mysql(sql)
        if len(result) == 0:
            return 1
        else:
            return 0


    def execute_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    # 회원가입 정보 insert
    def insert_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()

crud_user = CrudUser()