import os
from schemas.board import *
import db
from .base import Crudbase
from core.image import image
from models.board import Boards

db_server = db.db_server

class CrudBoard(Crudbase[Boards,int]):

    def create_board(self, writeBoard:CreateBoard):
        """
        새로운 게시글을 생성

        - writeBoard : 게시글의 요소들
            - user_id : user id
            - title : 제목
            - context : 내용
            - category : 카테고리
            - code : 코드
        """
        sql=[]
        data=[]

        sql.append("INSERT INTO `coco`.`boards` (`context`, `title`, `time`, `category`, `code`) VALUES (%s,%s,now(), %s, %s);")
        data.append((writeBoard.context, writeBoard.title, writeBoard.category, writeBoard.code))
        board_id=self.insert_last_id(sql,data)

        sql = "INSERT INTO `coco`.`boards_ids` (`board_id`, `user_id`) VALUES (%s, %s);"
        data=(board_id, writeBoard.user_id)
        self.execute_sql(sql,data)

        #게시글 내용에서 이미지의 url을 임시 url에서 진짜 url로 변경
        new_context=image.save_update_image(os.path.join(os.getenv("BOARD_PATH"),"temp",writeBoard.user_id),os.path.join(os.getenv("BOARD_PATH"),str(board_id)),writeBoard.context,board_id,"s")
        
        sql="UPDATE `coco`.`boards` SET `context` = %s WHERE (`id` = %s);"
        data=(new_context,board_id)
        self.execute_sql(sql,data)
    
        return 1

    def read_myboard(self, user_id):
        sql = "SELECT * FROM coco.view_board WHERE user_id = %s order by time desc;"
        data = user_id
        result = self.select_sql(sql, data)
        return result
    
    def read_board(self):
        '''
        게시글 정보 조회
        '''
        sql = 'SELECT * FROM coco.boards order by id desc'
        result = self.select_sql(sql)
        return result
    
    def read_board_with_pagination(self,info:PaginationIn):
        '''
        게시글 정보 조회
        '''
        sql = 'SELECT * FROM coco.boards order by id desc'
        total,result = self.select_sql_with_pagination(sql,size=info.size,page=info.page)

        return {"total":total,"size":info.size,"boardlist":result}

    def board_detail(self, board_id:int,user_id:str=None):
        '''
        특정 게시글 상세 정보 조회

        - board_id : 게시글 id
        - user_id : 조회를 요청한 유저의 id
        '''

        #게시글 조회수 증가
        update_views = "UPDATE `coco`.`boards` SET `views` = views+1 WHERE (`id` = %s);"
        data=(board_id)
        self.execute_sql(update_views,data)

        #게시글 정보 및 게시글 작성자 조회
        sql = """
            SELECT b.id, b.context, b.title, b.rel_task, b.time, 
            b.category, b.likes, b.views, b.comments, b.code, i.user_id 
            FROM coco.boards AS b, coco.boards_ids AS i
            WHERE b.id = i.board_id AND b.id = %s ;
        """
        data=(board_id)
        result = self.select_sql(sql,data)

        #게시글 댓글 정보 및 댓글 작성자 조회
        comments_sql = """
            SELECT c.id, c.context, c.write_time, c.likes, i.user_id, i.board_id
            FROM coco.comments AS c, coco.comments_ids AS i
            WHERE i.comment_id = c.id AND i.board_id = %s
            order by write_time desc;
        """
        data=(board_id)
        comments_result = self.select_sql(comments_sql,data)

        #조회를 요청한 유저가 댓글을 좋아요했는지 여부
        my_comment_like=[]
        if user_id:
            comment_liked_sql = """
            SELECT group_concat( i.comment_id) as liked
            FROM coco.comments_likes AS l, coco.comments_ids AS i, coco.boards AS b
            WHERE l.comment_id = i.comment_id AND b.id = %s AND l.user_id=%s group by l.user_id;
            """
            data = (board_id,user_id)
            comment_liked_result = self.select_sql(comment_liked_sql, data)
            if comment_liked_result:
                my_comment_like=list(map(int,comment_liked_result[0]["liked"].split(",")))
        for i in comments_result:
            if i["id"] in my_comment_like:
                i["is_liked"]=True
            else:
                i["is_liked"]=False

        #조회를 요청한 유저가 게시글을 좋아요했는지 여부
        is_board_liked=False
        if user_id:
            board_liked_sql = "SELECT user_id FROM coco.boards_likes WHERE boards_id = %s AND user_id = %s;"
            data = (board_id,user_id)
            is_board_liked = self.select_sql(board_liked_sql, data)
            if is_board_liked:
                is_board_liked=True
            else:
                is_board_liked=False

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
            'code': result[0]["code"],
            'user_id': result[0]["user_id"],
            'comments_datail': comments_result,
            'is_board_liked': is_board_liked,
        }

    def delete_board(self, board_id:int):
        """
        게시글 삭제

        - board_id : board id
        """
        comments_sql = "DELETE FROM coco.comments WHERE id in (select comment_id from coco.comments_ids where board_id=%s);"
        data=(board_id)
        self.execute_sql(comments_sql,data)
        board_sql = "DELETE FROM `coco`.`boards` WHERE (`id` = %s);"
        data=(board_id)
        self.execute_sql(board_sql,data)
        image.delete_image(os.path.join(os.getenv("BOARD_PATH"),str(board_id)))
        return 1

    def update_board_likes(self, boardLikes:LikesBase):
        """
        게시글의 좋아요 업데이트

        - boardLikes : 게시글의 요소들
            - user_id : user id
            - board_id : board id
            - type: True = 감소 , False = 증가
        - token : 사용자 인증
        """

        if boardLikes.type:
            update_sql = "UPDATE `coco`.`boards` SET `likes` = likes-1 WHERE (`id` = %s);"
            type_sql = "DELETE FROM `coco`.`boards_likes` WHERE (`user_id` = %s) and (`boards_id` = %s);"
        else:
            update_sql = "UPDATE `coco`.`boards` SET `likes` = likes+1 WHERE (`id` = %s);"
            type_sql = "INSERT INTO `coco`.`boards_likes` (`user_id`, `boards_id`) VALUES (%s, %s);" 
        update_data=(boardLikes.board_id)
        self.execute_sql(update_sql,update_data)
        type_data=(boardLikes.user_id,boardLikes.board_id)
        self.execute_sql(type_sql,type_data)
        return 1

    def create_comment(self, commentInfo:CreateComment):
        """
        새로운 댓글을 생성

        - commentInfo : 댓글의 요소들
            - user_id : user id
            - context : 댓글 내용
            - board_id : board id
        """
        sql=("INSERT INTO `coco`.`comments` (`context`, `write_time`) VALUES (%s, now());")
        data=((commentInfo.context))
        last_idx = self.insert_last_id([sql], [data])
        comment_sql = "INSERT INTO `coco`.`comments_ids` (`comment_id`, `user_id`, `board_id`) VALUES (%s, %s,%s);"
        data=(last_idx,commentInfo.user_id,commentInfo.board_id)
        self.execute_sql(comment_sql,data)

        sql="UPDATE `coco`.`boards` SET `comments` = `comments`+1 WHERE (`id` = %s);"
        data=(commentInfo.board_id)
        self.execute_sql(sql,data)
        return 1

    def delete_comment(self, board_id: int,comment_id: int):
        """
        댓글 삭제

        - board_id : board id
        - comment_id : comment id
        """
        comment_sql = "DELETE FROM `coco`.`comments` WHERE (`id` = %s);"
        data=(comment_id)
        self.execute_sql(comment_sql,data)
        
        sql="UPDATE `coco`.`boards` SET `comments` = `comments`-1 WHERE (`id` = %s);"
        data=(board_id)
        self.execute_sql(sql,data)
        return 1
    
    def update_comment_likes(self, commentLikes:CommentLikes):
        """
        댓글의 좋아요 업데이트

        - commentLikes : 댓글의 요소들
            - user_id : user id
            - board_id : board id
            - comment_id : comment id
            - type: True = 감소 , False = 증가
        """
        if commentLikes.type:
            update_sql = "UPDATE `coco`.`comments` SET `likes` = likes-1 WHERE (`id` = %s);"
            type_sql = "DELETE FROM `coco`.`comments_likes` WHERE (`user_id` = %s) and (`comment_id` = %s);"
        else:
            update_sql = "UPDATE `coco`.`comments` SET `likes` = likes+1 WHERE (`id` = %s);"
            type_sql = "INSERT INTO `coco`.`comments_likes` (`user_id`, `comment_id`) VALUES (%s, %s);" 
        update_data=(commentLikes.comment_id)
        self.execute_sql(update_sql,update_data)
        data=(commentLikes.user_id,commentLikes.comment_id)
        self.execute_sql(type_sql,data)

        return 1


board_crud=CrudBoard(Boards)
