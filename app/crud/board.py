import db
from datetime import datetime
from .base import Crudbase

db_server = db.db_server

class CrudBoard(Crudbase):
    def check_board(self):
        sql = 'select * from view_board order by time desc;'
        result = self.select_sql(sql)
        return result

    def board_detail(self, board_id):
        views_sql = "SELECT views FROM coco.boards WHERE id = %s;"
        data=(board_id)
        cnt_views = self.select_sql(views_sql,data)
        update_views = "UPDATE `coco`.`boards` SET `views` = %s WHERE (`id` = %s);"
        data=(cnt_views[0]["views"]+1,board_id)
        self.execute_sql(update_views,data)

        sql = """
            SELECT b.id, b.context, b.title, b.rel_task, b.time, 
            b.category, b.likes, b.views, b.comments, i.user_id, b.code
            FROM coco.boards AS b, coco.boards_ids AS i
            WHERE b.id = i.board_id AND b.id = %s;
        """
        data=(board_id)
        result = self.select_sql(sql,data)

        comments_sql = """
            SELECT c.id, c.context, c.write_time, c.likes, i.user_id, i.board_id
            FROM coco.comments AS c, coco.comments_ids AS i
            WHERE i.comment_id = c.id AND i.board_id = %s
            order by write_time desc;
        """
        data=(board_id)
        comments_result = self.select_sql(comments_sql,data)

        board_liked_sql = "SELECT user_id FROM coco.boards_likes WHERE boards_id = %s;"
        data = (board_id)
        board_liked_result = self.select_sql(board_liked_sql, data)

        board_liked_list = []
        for i in board_liked_result:
            board_liked_list.append(i['user_id'])

        comment_liked_sql = """
            SELECT l.user_id, i.comment_id
            FROM coco.comments_likes AS l, coco.comments_ids AS i, coco.boards AS b
            WHERE l.comment_id = i.comment_id AND b.id = %s;
        """
        data = (board_id)
        comment_liked_result = self.select_sql(comment_liked_sql, data)
        comment_liked_list = []
        for i in comment_liked_result:
            comment_liked_list.append([i['user_id'], i['comment_id']])

        return {
            'id': result[0]["id"],
            'context': result[0]["context"],
            'title': result[0]["title"],
            'rel_task': result[0]["rel_task"],
            'time': result[0]["time"],
            'category': result[0]["category"],
            'likes': result[0]["likes"],
            'views': result[0]["views"],
            'comments': result[0]["comments"],
            'user_id': result[0]["user_id"],
            'code': result[0]["code"],
            'comments_datail': comments_result,
            'is_board_liked': board_liked_list,
            'is_comment_liked': comment_liked_list
        }

    def write_board(self, writeBoard):
        print(writeBoard)
        sql = "INSERT INTO `coco`.`boards` (`context`, `title`, `time`, `category`, `likes`, `views`, `comments`, `code`) VALUES (%s,%s,%s, %s, '0', '0', '0', %s);"
        data=(writeBoard.context, writeBoard.title, datetime.now(), writeBoard.category, writeBoard.code)
        self.execute_sql(sql,data)
        user_sql = "SELECT * FROM coco.boards order by id;"
        result = self.select_sql(user_sql)
        board_sql = "INSERT INTO `coco`.`boards_ids` (`board_id`, `user_id`) VALUES (%s,%s);"
        data=(result[-1]["id"], writeBoard.user_id)
        self.execute_sql(board_sql,data)
        return 1

    def board_likes(self, boardLikes):
        update_sql = "UPDATE `coco`.`boards` SET `likes` = %s WHERE (`id` = %s);"
        data=(boardLikes.likes, boardLikes.board_id)
        self.execute_sql(update_sql,data)
        if boardLikes.type:
            type_sql = "DELETE FROM `coco`.`boards_likes` WHERE (`user_id` = %s) and (`boards_id` = %s);"
        else:
            type_sql = "INSERT INTO `coco`.`boards_likes` (`user_id`, `boards_id`) VALUES (%s, %s);" 
        data=(boardLikes.user_id,boardLikes.board_id)
        self.execute_sql(type_sql,data)

        return 1

    def write_comment(self, commentInfo):
        sql=[]
        data=[]
        sql.append("INSERT INTO `coco`.`comments` (`context`, `write_time`, `likes`) VALUES (%s, %s, '0');")
        data.append((commentInfo.context,datetime.now()))
        last_idx = self.insert_last_id(sql, data)
        comment_sql = "INSERT INTO `coco`.`comments_ids` (`comment_id`, `user_id`, `board_id`) VALUES (%s, %s,%s);"
        data=(last_idx,commentInfo.user_id,commentInfo.board_id)
        self.execute_sql(comment_sql,data)
        cnt_sql = """
            select count(*) as count from coco.comments_ids 
            where board_id = %s;
        """
        data=(commentInfo.board_id)
        cnt = self.select_sql(cnt_sql,data)
        update_sql = "UPDATE `coco`.`boards` SET `comments` = %s WHERE (`id` = %s);"
        data=(cnt[0]["count"],commentInfo.board_id)
        self.execute_sql(update_sql,data)
        return 1

    def comment_likes(self, commentLikes):
        update_sql = "UPDATE `coco`.`comments` SET `likes` = %s WHERE (`id` = %s);"
        data=(commentLikes.likes,commentLikes.comment_id)
        self.execute_sql(update_sql,data)
        if commentLikes.type:
            type_sql = "DELETE FROM `coco`.`comments_likes` WHERE (`user_id` = %s) and (`comment_id` = %s);"
        else:
            type_sql = "INSERT INTO `coco`.`comments_likes` (`user_id`, `comment_id`) VALUES (%s, %s);" 
        data=(commentLikes.user_id,commentLikes.comment_id)
        self.execute_sql(type_sql,data)

    def delete_content(self, board_id):
        comments_sql = "DELETE FROM coco.comments WHERE id in (select comment_id from coco.comments_ids where board_id=%s);"
        data=(board_id.board_id)
        self.execute_sql(comments_sql,data)
        board_sql = "DELETE FROM `coco`.`boards` WHERE (`id` = %s);"
        data=(board_id.board_id)
        self.execute_sql(board_sql,data)
        return 1

    def delete_comment(self, comment_id):
        comment_sql = "DELETE FROM `coco`.`comments` WHERE (`id` = %s);"
        data=(comment_id.comment_id)
        self.execute_sql(comment_sql,data)
        return 1

    def update_board(self, updateBoard):
        sql = "UPDATE coco.boards SET context = %s, title = %s WHERE (id = %s);"
        data = (updateBoard.context, updateBoard.title, updateBoard.board_id)
        self.execute_sql(sql,data)
        return 1

board_crud=CrudBoard()
