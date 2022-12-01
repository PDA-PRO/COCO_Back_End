import pymysql
import db

db_server = db.db_server

class CrudBoard():
    def check_board():
        sql = f'select * from contents;'
        result = CrudBoard.execute_mysql(sql)
        contents = []
        for i in result:
            content = {
                'id': i[0],
                'title': i[1],
                'user_id': i[2],
                'write_time': i[3],
                'category': i[4],
                'likes': i[5],
                'views': i[6],
                'comments': i[7]
            }
            contents.append(content)
        return contents

    def execute_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    def insert_mysql(query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()




crud_board = CrudBoard()