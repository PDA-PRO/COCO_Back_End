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

    def create(self,db_cursor:DBCursor,attributes:dict,db:str=None,table:str=None):
        """
        단순 INSERT문으로 튜플 생성 
        INSERT INTO db.table (attributes.keys) VALUES (attributes.values);

        params
        - db_cursor
        - attributes : 입력하려는 튜플의 속성값 ex) {"name":"name","id":"id"}
        - db : coco db를 제외한 다른 db에 접근
        - table : 지정한 :class:`ModelType`의 기본테이블을 제외한 다른 테이블에 접근
        ---------------
        returns
        - 1 : 정상종료시 반환
        """

        if not table:
            table=self.table
        if not db:
            table="coco."+table
        else:
            table=f"{db}.{table}"

        sql =f"insert into {table} "
        data=list(attributes.values())
        attributes="("+",".join(list(attributes.keys()))+")"
        string_format="("+",".join(["%s" for _ in range(len(data))])+")"
        sql +=attributes+" values "+string_format
        db_cursor.execute_sql(sql, data)
        return 1
    
    def read(self,db_cursor:DBCursor,attributes:list[str]=None,db:str=None,table:str=None,sort:bool=False,**conditions)->list[dict]:
        """
        단순 SELECT문으로 튜플 조회
        SELECT attributes FROM db.table WHERE conditions
        
        params
        - db_cursor
        - attributes : 조회하려는 튜플의 속성값, None 일 경우 모든 속성값 조회 ex) ["name","id"]
        - db : coco db를 제외한 다른 db에 접근        
        - table : 지정한 :class:`ModelType`의 기본테이블을 제외한 다른 테이블에 접근
        - sort : id값을 기준으로 조회결과값 내림차순 정렬
        - **conditions : 조회하려는 튜플의 조건 ex) name="name",id="id"
        ---------------
        returns
        - list : 결과값 유무에 관계없이 리스트 반환
        """
        if not attributes:
            attributes=["*"]

        #db및 스키마 설정
        if not table:
            table=self.table
        if not db:
            table="coco."+table
        else:
            table=f"{db}.{table}"

        #조회를 원하는 속성 추가
        sql="select "+",".join(attributes)+" from "+table

        #조건 추가
        condition_sql=[]
        data=[]
        if conditions:
            for condition,value in conditions.items():
                condition_sql.append(condition+"=%s ")
                data.append(value)
            sql+=" where "+"and ".join(condition_sql)
        if sort:
            sql+= " order by id desc "
        result = db_cursor.select_sql(sql,data)
        if not result:
            return []
        else:
            return result
        
    def read_with_pagination(self,db_cursor:DBCursor,attributes:list[str]=None,db:str=None,table:str=None,size:int=10, page:int=1,sort:bool=False)->tuple[int,list[dict]]:
        """
        단순 SELECT문으로 튜플 조회, 페이지네이션에 필요한 total, 제한된 결과값 조회
        SELECT attributes FROM db.table LIMIT size OFFSET (page-1)*size
        
        params
        - db_cursor
        - attributes : 조회하려는 튜플의 속성값, None 일 경우 모든 속성값 조회 ex) ["name","id"]
        - db : coco db를 제외한 다른 db에 접근        
        - table : 지정한 :class:`ModelType`의 기본테이블을 제외한 다른 테이블에 접근
        - size : 한 페이지의 크기
        - page : 현재 페이지의 번호
        - sort : id값을 기준으로 조회결과값 내림차순 정렬
        ---------------
        returns
        - total : 전체 튜플 개수 
        - list : 결과값 유무에 관계없이 리스트 반환
        """
        if not attributes:
            attributes=["*"]

        #db및 스키마 설정
        if not table:
            table=self.table
        if not db:
            table="coco."+table
        else:
            table=f"{db}.{table}"

        sql="select "+",".join(attributes)+" from "+table
        
        if sort:
            sql+= " order by id desc "

        total,result = db_cursor.select_sql_with_pagination(sql,size=size,page=page)
        if total<=0:
            return total,[]
        else:
            return total,result
        
    def update(self,db_cursor:DBCursor,attributes:dict,db:str=None,table:str=None,**conditions):
        """
        단순 UPDATE문으로 튜플 생성 
        UPDATE db.table SET attributes WHERE conditions;

        params
        - db_cursor
        - attributes : 수정하려는 튜플의 속성값 ex) {"name":"name","id":"id"}
        - db : coco db를 제외한 다른 db에 접근
        - table : 지정한 :class:`ModelType`의 기본테이블을 제외한 다른 테이블에 접근
        - **conditions : 수정하려는 튜플의 조건 ex) name="name",id="id"
        ---------------
        raise
        - ValueError : conditions값이 존재하지 않을 때
        ---------------
        returns
        - 1 : 정상종료시 반환
        """
        if not conditions:
            raise ValueError("condition값이 존재하지 않습니다. 수정할 튜플의 조건을 입력해주세요")
        if not table:
            table=self.table
        if not db:
            table="coco."+table
        else:
            table=f"{db}.{table}"

        sql =f"update {table} set "
        data=[]
        attribute_sql=[]
        for attribute,value in attributes.items():
            attribute_sql.append(attribute+"=%s ")
            data.append(value)

        sql+=",".join(attribute_sql)+" where "

        #조건 추가
        condition_sql=[]
        for condition,value in conditions.items():
            condition_sql.append(condition+"=%s ")
            data.append(value)
        sql+="and ".join(condition_sql)

        db_cursor.execute_sql(sql, data)
        return 1

    def delete(self,db_cursor:DBCursor,db:str=None,table:str=None,**conditions):
        """
        단순 DELETE문으로 튜플 생성 
        DELETE FROM db.table WHERE conditions;

        params
        - db_cursor
        - attributes : 삭제하려는 튜플의 속성값 ex) {"name":"name","id":"id"}
        - db : coco db를 제외한 다른 db에 접근
        - table : 지정한 :class:`ModelType`의 기본테이블을 제외한 다른 테이블에 접근
        - **conditions : 삭제하려는 튜플의 조건 ex) name="name",id="id"
        ---------------
        raise
        - ValueError : conditions값이 존재하지 않을 때
        ---------------
        returns
        - 1 : 정상종료시 반환
        """
        
        if not conditions:
            raise ValueError("condition값이 존재하지 않습니다. 삭제할 튜플의 조건을 입력해주세요")
        if not table:
            table=self.table
        if not db:
            table="coco."+table
        else:
            table=f"{db}.{table}"

        sql ="delete from "+table+" where "
        data=[]

        #조건 추가
        condition_sql=[]
        for condition,value in conditions.items():
            condition_sql.append(condition+"=%s ")
            data.append(value)
        sql+="and ".join(condition_sql)

        db_cursor.execute_sql(sql, data)
        return 1