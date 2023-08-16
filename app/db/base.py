from pymysql.cursors import Cursor

class DBCursor():
    def __init__(self,cursor:Cursor) -> None:
        self.cursor=cursor

    def select_sql(self,query:str,data:tuple=None):
        """
        1개의 쿼리 실행 후 출력 값 리턴
        
        - query : 쿼리문
        - data : 쿼리문에 들어갈 데이터
        """
        self.cursor.execute(query,data)
        result = self.cursor.fetchall()
        return result

    def execute_sql(self, query:str,data:tuple=None):
        """
        1개의 쿼리 실행 리턴 값 없음
        
        - query : 쿼리문
        - data : 쿼리문에 들어갈 데이터
        """
        self.cursor.execute(query,data)

    def insert_last_id(self,query:list[str],data:list[tuple]):
        """
        id속성에 auto increment가 적용된 테이블에 대해
        여러 개의 쿼리 실행 후 마지막 id값 리턴
        
        - query : 쿼리문 리스트
        - data : 쿼리문에 들어갈 데이터 리스트
        """
        for i in range(len(query)):
            self.cursor.execute(query[i],data[i])
        self.cursor.execute("select LAST_INSERT_ID() as id;")
        id=self.cursor.fetchall()
        return id[0]["id"]
    
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
        self.cursor.execute(query,data)
        total = len(self.cursor.fetchall())
        
        query+=" limit %s offset %s;"
        data = (*data, size,(page-1)*size)
        self.cursor.execute(query,data)
        result = self.cursor.fetchall()
        return total,result