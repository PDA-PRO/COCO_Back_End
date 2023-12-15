import os

from fastapi import HTTPException
from app.schemas.board import *
from .base import Crudbase
from app.core.image import image
from app.models.board import Boards
from app.db.base import DBCursor
from app.crud.alarm import alarm_crud

class CrudBoard(Crudbase[Boards,int]):
    def create_board(self,db_cursor:DBCursor, writeBoard:BoardBody, user_id:str):
        """
        새로운 게시글을 생성

        params
        - writeBoard : 게시글의 요소들
            - title : 제목
            - context : 내용
            - category : 카테고리
            - code : 코드
        - user_id : 글쓴이 id
        -----------------------------
        return
        - 성공시 게시글 id 반환
        """
        sql="INSERT INTO `coco`.`boards` (`context`, `title`, `time`, `category`, `code`) VALUES (%s,%s,now(), %s, %s);"
        data=(writeBoard.context, writeBoard.title, writeBoard.category, writeBoard.code)
        board_id=db_cursor.insert_last_id(sql,data)

        sql = "INSERT INTO `coco`.`boards_ids` (`board_id`, `user_id`) VALUES (%s, %s);"
        data=(board_id, user_id)
        db_cursor.execute_sql(sql,data)

        #게시글 내용에서 이미지의 url을 임시 url에서 진짜 url로 변경
        new_context=image.save_update_image(os.path.join(os.getenv("BOARD_PATH"),"temp",user_id),os.path.join(os.getenv("BOARD_PATH"),str(board_id)),writeBoard.context,board_id,"s")
        
        sql="UPDATE `coco`.`boards` SET `context` = %s WHERE (`id` = %s);"
        data=(new_context,board_id)
        db_cursor.execute_sql(sql,data)
    
        return board_id

    def read_myboard(self,db_cursor:DBCursor, user_id:str):
        """
        해당 user가 쓴 게시글 목록 조회

        params
        - user_id : 글쓴이 id
        -----------------------------
        return
        - 성공시 게시글 목록
        """
        sql = "SELECT * FROM coco.view_board WHERE user_id = %s order by time desc;"
        data = user_id
        result = db_cursor.select_sql(sql, data)
        return result

    def board_detail(self, db_cursor:DBCursor,board_id:int,user_id:str=None):
        '''
        특정 게시글 상세 정보 조회
        유저 id가 존재한다면 해당 유저가 게시글을 좋아요 했는지 정보 표시

        params
        - board_id : 게시글 id
        - user_id : 조회를 요청한 유저의 id
        ----------------------------------------
        return
        - 성공시 게시글 상세 정보 목록
        '''

        #게시글 정보 및 게시글 작성자 조회
        sql = """
            SELECT b.id, b.context, b.title, b.rel_task, b.time, 
            b.category, b.likes, b.views, b.comments, b.code, i.user_id 
            FROM coco.boards AS b, coco.boards_ids AS i
            WHERE b.id = i.board_id AND b.id = %s ;
        """
        data=(board_id)
        result = db_cursor.select_sql(sql,data)

        if len(result) == 0:
            raise HTTPException(
                status_code=404,
                detail="존재하지 않는 게시글입니다",
                headers={"WWW-Authenticate": "Bearer"},
            )

        #게시글 조회수 증가
        update_views = "UPDATE `coco`.`boards` SET `views` = views+1 WHERE (`id` = %s);"
        data=(board_id)
        db_cursor.execute_sql(update_views,data)


        #조회를 요청한 유저가 게시글을 좋아요했는지 여부
        is_board_liked=False
        if user_id:
            board_liked_sql = "SELECT user_id FROM coco.boards_likes WHERE boards_id = %s AND user_id = %s;"
            data = (board_id,user_id)
            is_board_liked = db_cursor.select_sql(board_liked_sql, data)
            if is_board_liked:
                is_board_liked=True
            else:
                is_board_liked=False

        return {
            **result[0],
            'is_board_liked': is_board_liked,
        }

    def update_board(self, db_cursor:DBCursor, board_id:int,info:BoardBody):
        if info.code == None:
            sql = "UPDATE `coco`.`boards` SET `context` = %s, `title` = %s WHERE (`id` = %s);"
            data = (info.context, info.title, board_id)
        else:
            sql = "UPDATE `coco`.`boards` SET `context` = %s, `title` = %s, `code` = %s WHERE (`id` = %s);"
            data = (info.context, info.title, info.code, board_id)
        db_cursor.execute_sql(sql, data)
        return {'id': board_id}
    
    def delete_board(self,db_cursor:DBCursor, board_id:int):
        """
        게시글 삭제

        params
        - board_id : board id
        -----------------------
        return
        - 성공시 1
        """
        comments_sql = "DELETE FROM coco.comments WHERE id in (select comment_id from coco.comments_ids where board_id=%s);"
        data=(board_id)
        db_cursor.execute_sql(comments_sql,data)
        board_sql = "DELETE FROM `coco`.`boards` WHERE (`id` = %s);"
        data=(board_id)
        db_cursor.execute_sql(board_sql,data)
        image.delete_image(os.path.join(os.getenv("BOARD_PATH"),str(board_id)))
        return 1

    def update_board_likes(self,db_cursor:DBCursor, board_id:int,like_type:bool, user_id:str):
        """
        게시글의 좋아요 업데이트

        params
        - board_id : board id
        - like_type: True = 감소 , False = 증가
        - user_id : user id
        ---------------------------------
        return
        - 성공시 1
        """

        if like_type:
            update_sql = "UPDATE `coco`.`boards` SET `likes` = likes-1 WHERE (`id` = %s);"
            type_sql = "DELETE FROM `coco`.`boards_likes` WHERE (`user_id` = %s) and (`boards_id` = %s);"
        else:
            update_sql = "UPDATE `coco`.`boards` SET `likes` = likes+1 WHERE (`id` = %s);"
            type_sql = "INSERT INTO `coco`.`boards_likes` (`user_id`, `boards_id`) VALUES (%s, %s);" 
        update_data=(board_id)
        db_cursor.execute_sql(update_sql,update_data)
        type_data=(user_id,board_id)
        db_cursor.execute_sql(type_sql,type_data)

        board_writer_sql = "select user_id from `coco`.`boards_ids` where board_id = %s"
        board_writer_data = (board_id)
        board_writer_result = db_cursor.select_sql(board_writer_sql, board_writer_data)

        if not like_type:
            alarm_crud.create_alarm(
                db_cursor, 
                {
                    'sender':user_id, 'receiver': board_writer_result[0]['user_id'], 
                    'context': { 'board_id': board_id }, 
                    'category': 2
                }
            )
        return 1

    def read_comment(self,db_cursor:DBCursor,board_id:CreateComment,user_id:str):
        '''
        해당 게시글의 댓글 정보 리스트 조회
        유저 id가 존재한다면 해당 유저가 댓글을 좋아요 했는지 정보 표시

        params
        - board_id
        - user_id : 조회한 유저 id
        ---------------------------------
        returns
        - 댓글 정보 리스트
        '''
        #게시글 댓글 정보 및 댓글 작성자 조회
        comments_sql = """
            SELECT c.id, c.context, c.write_time, c.likes, i.user_id, i.board_id
            FROM coco.comments AS c, coco.comments_ids AS i
            WHERE i.comment_id = c.id AND i.board_id = %s
            order by write_time desc;
        """
        data=(board_id)
        comments_result = db_cursor.select_sql(comments_sql,data)

        #조회를 요청한 유저가 댓글을 좋아요했는지 여부
        my_comment_like=[]
        if user_id:
            comment_liked_sql = """
            SELECT group_concat( i.comment_id) as liked
            FROM coco.comments_likes AS l, coco.comments_ids AS i, coco.boards AS b
            WHERE l.comment_id = i.comment_id AND b.id = %s AND l.user_id=%s group by l.user_id;
            """
            data = (board_id,user_id)
            comment_liked_result = db_cursor.select_sql(comment_liked_sql, data)
            if comment_liked_result:
                my_comment_like=list(map(int,comment_liked_result[0]["liked"].split(",")))
        for i in comments_result:
            if i["id"] in my_comment_like:
                i["is_liked"]=True
            else:
                i["is_liked"]=False
        return comments_result

    def create_comment(self, db_cursor:DBCursor,board_id: int,commentInfo:CreateComment,user_id:str):
        """
        새로운 댓글을 생성

        params
        - board_id : board id
        - commentInfo
            - context : 댓글 내용
        - user_id : user id
        ---------------------------
        returns
        - 생성된 댓글의 id
        """
        sql="INSERT INTO `coco`.`comments` (`context`, `write_time`) VALUES (%s, now());"
        data=(commentInfo.context)
        last_idx = db_cursor.insert_last_id(sql, data)
        comment_sql = "INSERT INTO `coco`.`comments_ids` (`comment_id`, `user_id`, `board_id`) VALUES (%s, %s,%s);"
        data=(last_idx,user_id,board_id)
        db_cursor.execute_sql(comment_sql,data)

        sql="UPDATE `coco`.`boards` SET `comments` = `comments`+1 WHERE (`id` = %s);"
        data=(board_id)
        db_cursor.execute_sql(sql,data)

        board_writer_sql = "select user_id from `coco`.`boards_ids` where board_id = %s"
        board_writer_data = (board_id)
        board_writer_result = db_cursor.select_sql(board_writer_sql, board_writer_data)
        
        alarm_crud.create_alarm(
            db_cursor, 
            {
                'sender':user_id, 'receiver': board_writer_result[0]['user_id'], 
                'context': { 'board_id': board_id }, 
                'category': 1
            }
        )
        return last_idx

    def delete_comment(self, db_cursor:DBCursor,board_id: int,comment_id: int):
        """
        댓글 삭제

        params
        - board_id : board id
        - comment_id : comment id
        -----------------------
        return
        - 성공시 1
        """
        comment_sql = "DELETE FROM `coco`.`comments` WHERE (`id` = %s);"
        data=(comment_id)
        db_cursor.execute_sql(comment_sql,data)
        
        sql="UPDATE `coco`.`boards` SET `comments` = `comments`-1 WHERE (`id` = %s);"
        data=(board_id)
        db_cursor.execute_sql(sql,data)
        return 1
    
    def update_comment_likes(self,db_cursor:DBCursor, board_id: int,comment_id: int,like_type:bool,user_id:str):
        """
        댓글의 좋아요 업데이트

        params
        - board_id : board id
        - comment_id : comment id
        - like_type: True = 감소 , False = 증가
        - user_id : user id
        -----------------------------
        return
        - 성공시 1
        """
        if like_type:
            update_sql = "UPDATE `coco`.`comments` SET `likes` = likes-1 WHERE (`id` = %s);"
            type_sql = "DELETE FROM `coco`.`comments_likes` WHERE (`user_id` = %s) and (`comment_id` = %s);"
        else:
            update_sql = "UPDATE `coco`.`comments` SET `likes` = likes+1 WHERE (`id` = %s);"
            type_sql = "INSERT INTO `coco`.`comments_likes` (`user_id`, `comment_id`) VALUES (%s, %s);" 
        update_data=(comment_id)
        db_cursor.execute_sql(update_sql,update_data)
        data=(user_id,comment_id)
        db_cursor.execute_sql(type_sql,data)

        #좋아요 눌리면
        if not like_type:
            # 댓글 좋아요 알람
            com_writer_sql = "select user_id from `coco`.`comments_ids` where comment_id = %s"
            com_writer_data = (comment_id)
            com_writer_result = db_cursor.select_sql(com_writer_sql, com_writer_data)
            alarm_crud.create_alarm(
                db_cursor, 
                {
                    'sender':user_id, 'receiver': com_writer_result[0]['user_id'], 
                    'context': { 'board_id': board_id }, 
                    'category': 3
                }
            )

        return 1


board_crud=CrudBoard(Boards)
