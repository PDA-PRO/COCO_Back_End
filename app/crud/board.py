import pymysql
import db

db_server = db.db_server

class CrudBoard():
    def check_board(self):
        sql = f'select * from view_board'
        result = self.execute_mysql(sql)
        contents = []
        for i in result:
            content = {
                'board_id': i[0],
                'title': i[1],
                'time': i[2],
                'category': i[3],
                'likes': i[4],
                'views': i[5],
                'comments': i[6],
                'user_id': i[7],
            }
            contents.append(content)
        return contents

    def board_detail(self, board_id):
        print(board_id)
        sql = f"SELECT * FROM coco.boards where id = '{board_id}';"
        result = self.execute_mysql(sql)
        return {
            'id': result[0][0],
            'contest': result[0][1],
            'title': result[0][2],
            'rel_task': result[0][3],
            'time': result[0][4],
            'category': result[0][5],
            'likes': result[0][6],
            'views': result[0][7],
            'comments': result[0][8]
        }

    def execute_mysql(self, query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        con.close()
        return result

    def insert_mysql(self, query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        con.commit()
        con.close()
