import pymysql
import db

db_server = db.db_server

class Crudbase():
    def select_sql(self, query:str,data:tuple=None,return_dict:bool=True):
        """
        1개의 쿼리 실행 후 출력 값 리턴
        
        - query : 쿼리문
        - data : 쿼리문에 들어갈 데이터
        - return_dict : 결과값을 dict 자료형으로 반환
        """
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        if return_dict:
            cur = con.cursor(pymysql.cursors.DictCursor)
        else:
            cur = con.cursor()
        cur.execute(query,data)
        result = cur.fetchall()
        con.close()
        return result

    def execute_sql(self, query:str,data:tuple=None):
        """
        1개의 쿼리 실행 리턴 값 없음
        
        - query : 쿼리문
        - data : 쿼리문에 들어갈 데이터
        """
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query,data)
        con.commit()
        con.close()

    def insert_last_id(self,query:list[str],data:list[tuple]):
        """
        id속성에 auto increment가 적용된 테이블에 대해
        여러 개의 쿼리 실행 후 마지막 id값 리턴
        
        - query : 쿼리문 리스트
        - data : 쿼리문에 들어갈 데이터 리스트
        """
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)
        for i in range(len(query)):
            cur.execute(query[i],data[i])
        cur.execute("select LAST_INSERT_ID() as id;")
        id=cur.fetchall()
        con.commit()
        con.close()
        return id[0]["id"]
    
    def reset_auto_increment(self, cnt_query, reset_query):
        print(cnt_query, reset_query)
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                    db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(cnt_query)
        row_cnt = cur.fetchall()
        print(row_cnt[0][0])
        if row_cnt[0][0] == 0:
            cur.execute(reset_query)
        con.commit()
        con.close()

    def group_ai_reset(self, query, data):
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                            db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor()
        cur.execute(query[0])
        cur.execute(query[1])
        cur.execute(query[2], data)
        con.commit()
        con.close()

    def select_sql_with_pagination(self, query:str,data:tuple=tuple(),size:int=10, page:int=1,)->tuple[int,list]:
        """
        1개의 쿼리문을 페이지네이션으로 실행
        
        param
        - query : 쿼리문 리스트
        - data : 쿼리문에 들어갈 데이터 리스트
        - size : 한 페이지의 크기
        - page : 현재 페이지의 번호
        ----------------------------------
        return
        - total : 기존 쿼리 결과의 전체 개수
        - result : 페이지네이션된 결과값
        """
        
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                    db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)
        cur.execute(query,data)
        total = len(cur.fetchall())
        
        query+=" limit %s offset %s;"
        data = (*data, size,(page-1)*size)
        cur.execute(query,data)
        result = cur.fetchall()
        con.close()
        return total,result
        



