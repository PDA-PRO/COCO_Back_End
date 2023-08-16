import pymysql
import db
from typing import Generic, TypeVar
from db.base import DBCursor
ModelType = TypeVar("ModelType")
IdType=TypeVar("IdType")

db_server = db.db_server

class Crudbase(Generic[ModelType,IdType]):
    def __init__(self,model:ModelType=None) -> None:
        super().__init__()
        if model:
            self.model=model
            self.table=str(model).split(".")[-1].split("'")[0].lower()
        else:
            self.model=None
            self.table=None
        
    def validate_attr(self,attribute:list[str]) -> bool:
        """
        조회하려는 속성이 테이블에 존재하는지 확인
        존재하지 않는 속성 조회시 에러 발생
        
        param
        - attribute : 속성 리스트
        """
        none_attr=[]
        if self.model:
            exist_attr=self.model.__annotations__.keys()
            for i in attribute:
                if i not in exist_attr:
                    none_attr.append(i)
            if none_attr:
                raise ValueError(str(self.model)+"에서 존재하지 않는 속성값 ["+",".join(none_attr)+"] 을 요청하였습니다.")
        else:
            raise ReferenceError("self.model이 존재하지 않습니다.")
        return True

    def read(self,db_cursor:DBCursor,id,attribute:list[str]=None, strict:bool=False)->dict|None:
        """
        id에 해당하는 튜플의 속성값 조회
        값이 없다면 None 리턴
        존재하지 않는 속성 조회시 에러 발생
        
        param
        - id : 튜플 id
        - attribute : 속성 리스트 | 아무것도 작성하지 않을 때는 모든 속성값 조회
        - strict : 속성 유무 확인 
        -------------------------
        return
        - result : 튜플의 값 딕셔너리
        """
        if attribute and strict:
            self.validate_attr(attribute)
        else:
            attribute=self.model.__annotations__.keys()
        sql="select id "
        sql+=",".join(attribute)
        sql+=" from coco."+self.table+" where id=%s"
        
        db_cursor.execute(sql,[id])
        result = db_cursor.fetchall()
        if not result:
            return None
        else:
            return result[0]
        
    def read_with_pagination(self,db_cursor:DBCursor,attribute:list[str]=None,size:int=10, page:int=1,strict:bool=False)->tuple[int,list[dict]]:
        """
        모든 튜플의 속성값을 페이지네이션으로 조회

        존재하지 않는 속성 조회시 에러 발생
        
        param
        - attribute : 속성 리스트 | 아무것도 작성하지 않을 때는 모든 속성값 조회
        - size : 한 페이지의 크기
        - page : 현재 페이지 번호
        - strict : 속성 유무 확인 
        ------------------------
        return
        - total : 전체 값 개수
        - result : 튜플의 값 리스트
        """
        if attribute and strict:
            self.validate_attr(attribute)
        else:
            attribute=self.model.__annotations__.keys()

        #페이지네이션 전 결과 개수 조회
        sql="select id "+",".join(attribute)+" from coco."+self.table
        db_cursor.execute(sql)
        total = len(db_cursor.fetchall())

        #페이지네이션 후 결과 조회
        sql+=" limit %s offset %s;"
        db_cursor.execute(sql,[size,(page-1)*size])
        result = db_cursor.fetchall()
        if total<=0:
            return total,[]
        else:
            return total,result