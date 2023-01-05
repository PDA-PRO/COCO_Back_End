from .base import Crudbase
import db

db_server = db.db_server

class CrudMyPage(Crudbase):
    def myboard(self, user_id):
        sql = "SELECT * FROM coco.view_board WHERE user_id = %s;"
        data = user_id
        result = self.select_sql(sql, data)
        return result


mypage = CrudMyPage()