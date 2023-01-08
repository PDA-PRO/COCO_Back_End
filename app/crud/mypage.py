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

    def myboard(self, user_id):
        sql = "SELECT * FROM coco.view_board WHERE user_id = %s;"
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




mypage = CrudMyPage()