import pymysql
import db
from datetime import datetime

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
        comments_sql = f"""
            SELECT c.id, c.context, c.write_time, c.likes, i.user_id, i.board_id
            FROM coco.comments AS c, comments_ids AS i
            WHERE i.comment_id = c.id AND i.board_id = '{board_id}';
        """
        comments_result = self.execute_mysql(comments_sql)

        return {
            'id': result[0][0],
            'context': result[0][1],
            'title': result[0][2],
            'rel_task': result[0][3],
            'time': result[0][4],
            'category': result[0][5],
            'likes': result[0][6],
            'views': result[0][7],
            'comments': result[0][8],
            'comments_datail': comments_result
        }

    def fast_write(self, fastWrite):
        sql = f"INSERT INTO `coco`.`boards` (`context`, `title`, `time`, `category`, `likes`, `views`, `comments`) VALUES ('{fastWrite.context}', '{fastWrite.title}', '{datetime.now().date()}', '3', '0', '0', '0');"
        self.insert_mysql(sql)
        user_sql = f"SELECT * FROM coco.boards order by id;"
        result = self.execute_mysql(user_sql)
        board_sql = f"INSERT INTO `coco`.`boards_ids` (`board_id`, `user_id`) VALUES ('{result[-1][0]}', '{fastWrite.user_id}');"
        self.insert_mysql(board_sql)
        return 1

    def board_likes(self, boardLikes):
        update_sql = f"UPDATE `coco`.`boards` SET `likes` = '{boardLikes.likes}' WHERE (`id` = '{boardLikes.board_id}');"
        self.insert_mysql(update_sql)
        type_sql = ""
        if boardLikes.type:
            type_sql = f"DELETE FROM `coco`.`boards_likes` WHERE (`user_id` = '{boardLikes.user_id}') and (`boards_id` = '{boardLikes.board_id}');"
        else:
            type_sql = f"INSERT INTO `coco`.`boards_likes` (`user_id`, `boards_id`) VALUES ('{boardLikes.user_id}', '{boardLikes.board_id}');" 
        self.insert_mysql(type_sql)
        return 1

    def write_comment(self, commentInfo):
        print(commentInfo)
        sql = f"INSERT INTO `coco`.`comments` (`context`, `write_time`, `likes`) VALUES ('{commentInfo.context}', '{datetime.now().date()}', '0');"
        idx_sql  = f"select LAST_INSERT_ID();"
        last_idx = self.insert_comments(sql, idx_sql)
        comment_sql = f"INSERT INTO `coco`.`comments_ids` (`comment_id`, `user_id`, `board_id`) VALUES ('{last_idx}', '{commentInfo.user_id}', '{commentInfo.board_id}');"
        self.insert_mysql(comment_sql)
        return 1

    def comment_likes(self, commentLikes):
        update_sql = f"UPDATE `coco`.`comments` SET `likes` = '{commentLikes.likes}' WHERE (`id` = '{commentLikes.comment_id}');"
        self.insert_mysql(update_sql)
        type_sql = ""
        if commentLikes.type:
            type_sql = f"DELETE FROM `coco`.`comments_likes` WHERE (`user_id` = '{commentLikes.user_id}') and (`comment_id` = '{commentLikes.comment_id}');"
        else:
            type_sql = f"INSERT INTO `coco`.`comments_likes` (`user_id`, `comment_id`) VALUES ('{commentLikes.user_id}', '{commentLikes.comment_id}');" 
        self.insert_mysql(type_sql)

    def insert_comments(self, query, idx_query):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query)
        cur.execute(idx_query)
        idx = cur.fetchall()
        con.commit()
        con.close()
        return idx[0][0]

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
    

