import pymysql
import db
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType")
IdType=TypeVar("IdType")

db_server = db.db_server

class Crudbase(Generic[ModelType,IdType]):
    def __init__(self,model:ModelType=None) -> None:
        super().__init__()
        if model:
            self.model=model
            self.table=str(model).split(".")[-1].split("'")[0].lower()
        
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
        
    def validate_attr(self,attribute:list[str]) -> bool:
        """
        조회하려는 속성이 테이블에 존재하는지 확인
        존재하지 않는 속성 조회시 에러 발생
        
        param
        - attribute : 속성 리스트
        """
        none_attr=[]
        exist_attr=self.model.__annotations__.keys()
        for i in attribute:
            if i not in exist_attr:
                none_attr.append(i)
        if none_attr:
            raise ValueError(str(self.model)+"에서 존재하지 않는 속성값 ["+",".join(none_attr)+"] 을 요청하였습니다.")
        return True

    def read(self,id:IdType,attribute:list[str]=None)->dict|None:
        """
        id에 해당하는 튜플의 속성값 조회
        값이 없다면 None 리턴
        존재하지 않는 속성 조회시 에러 발생
        
        param
        - id : 튜플 id
        - attribute : 속성 리스트 | 아무것도 작성하지 않을 때는 모든 속성값 조회
        -------------------------
        return
        - result : 튜플의 값 딕셔너리
        """
        if attribute:
            self.validate_attr(attribute)
        else:
            attribute=self.model.__annotations__.keys()
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                    db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)
        sql="select id "
        sql+=",".join(attribute)
        sql+=" from coco."+self.table+" where id=%s"
        
        cur.execute(sql,[id])
        result = cur.fetchall()
        con.close()
        if not result:
            return None
        else:
            return result[0]
        
    def read_with_pagination(self,attribute:list[str]=None,size:int=10, page:int=1)->tuple[int,list[dict]]:
        """
        모든 튜플의 속성값을 페이지네이션으로 조회

        존재하지 않는 속성 조회시 에러 발생
        
        param
        - attribute : 속성 리스트 | 아무것도 작성하지 않을 때는 모든 속성값 조회
        - size : 한 페이지의 크기
        - page : 현재 페이지 번호
        ------------------------
        return
        - total : 전체 값 개수
        - result : 튜플의 값 리스트
        """
        if attribute:
            self.validate_attr(attribute)
        else:
            attribute=self.model.__annotations__.keys()
        con = pymysql.connect(host=db_server.host, user=db_server.user, password=db_server.password,port=db_server.port,
                    db=db_server.db, charset='utf8')  # 한글처리 (charset = 'utf8')
        cur = con.cursor(pymysql.cursors.DictCursor)

        #페이지네이션 전 결과 개수 조회
        sql="select id "+",".join(attribute)+" from coco."+self.table
        cur.execute(sql)
        total = len(cur.fetchall())

        #페이지네이션 후 결과 조회
        sql+=" limit %s offset %s;"
        cur.execute(sql,[size,(page-1)*size])
        result = cur.fetchall()
        con.close()
        if total<=0:
            return total,[]
        else:
            return total,result