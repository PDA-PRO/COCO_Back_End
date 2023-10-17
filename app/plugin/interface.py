from abc import *
from fastapi import Depends
from app.api.deps import get_cursor
from contextlib import contextmanager

from app.db.base import DBCursor

class AbstractPlugin(metaclass=ABCMeta):
    '''
    ai 플러그인 추상클래스
    해당 `AbstractPlugin`를 상속받아 `Plugin`이름의 클래스 구현 필요

    세부구현이 필요한 내부클래스
    - `TableModel` : `AbstractPlugin.AbstractTable`을 상속하는 클래스로써 ai플러그인 db 저장소 정의

    정의가 필요한 클래스변수
    - `router_path` : ai플러그인 엔드포인트 접두사

    세부구현이 필요한 함수
    - `test` : ai플러그인 테스트
    - `main` : ai플러그인 메인동작
    '''

    router_path=''

    @staticmethod
    @abstractmethod
    def test():
        '''
        ai 플러그인이 사용가능한지 테스트

        -----------------------------
        returns
        - 사용가능하지 않다면 `False`, 사용가능하다면 `True`
        '''
        pass

    @staticmethod
    @abstractmethod
    def main(db_cursor:DBCursor=Depends(get_cursor)):
        '''
        ai 플러그인의 메인 동작을 구현

        -----------------------------
        params
        - db_cursor : db에 조작을 위한 cursor
        '''
        pass
    
    class AbstractTable():
        '''
        TableModel의 이름의 클래스 명시 필수

        ai 플러그인의 테이블 스키마 명시
        예시, ::

          #클래스 명과 상속 클래스 고정
          class TableModel(AbstractPlugin.AbstractTable):
              __key__='sub_id' #다중키일 경우 ['sub_id','status'] *필수
              __tablename__='wpc' #테이블이름 *필수
              sub_id:int #속성이름:속성타입 속성타입은 str과 int만 가능
              status:int
              result:str
              ...

        '''
        def __init__(self,**values) -> None:
            assert_key_list=[]
            if type(self.__class__.__key__)==list:
                assert_key_list=self.__class__.__key__
            else:
                assert_key_list.append(self.__class__.__key__)
            for i in self.__annotations__.items():
                if i[0] in assert_key_list:
                    assert type(values.get(i[0]))==int, "속성값 타입 에러"
                else:
                    assert values.get(i[0])==None or i[1]==type(values.get(i[0])), "속성값 타입 에러"
                self.__setattr__(i[0],values.get(i[0]))

        def __str__(self) -> str:
            return str(self.__dict__)
        
        def __repr__(self) -> str:
            return str(self.__dict__)


    ###
    ### 동작을 위한 클래스
    ###

    type_list={
        int:"int",
        str:"text"
    }

    @classmethod
    def creat_table(cls):
        '''
        ai 플러그인 db 저장소 테이블 생성
        '''
        col_type_list=[]
        key_list=cls.validate_key()
        
        for i in cls.TableModel.__annotations__.items():
            temp_col_type=""
            col_type=cls.type_list.get(i[1])
            if col_type:
                temp_col_type=f"`{i[0]}` {col_type}"
            else:
                raise Exception("지원하지 않는 속성 타입입니다.")
            
            if i[0] in key_list :
                col_type_list.append(temp_col_type+" not null")
            else:
                col_type_list.append(temp_col_type)
        table_name=cls.TableModel.__tablename__
        
        sql=f'''
        CREATE TABLE IF NOT EXISTS `plugin`.`{table_name}` (
            {", ".join(col_type_list)},
            PRIMARY KEY ({", ".join(key_list)}));
            '''

        with contextmanager(get_cursor)() as curosr:
            curosr.execute_sql(sql)

    @classmethod
    def read_all(cls,db_cursor:DBCursor)->list:
        '''
        Plugin 클래스 클래스 메소드

        ai 플러그인 db 저장소에서 모든 튜플 조회

        params
        - db_cursor : db 조작을 위한 curosor

        사용예시
        .. code-block:: python

        Plugin.read_all(db_cursor)

        '''
        table_name=cls.TableModel.__tablename__
        sql=f'''
        SELECT * FROM plugin.{table_name};
            '''
        return_value=[]
        for i in db_cursor.select_sql(sql):
            return_value.append(cls.TableModel(**i))
            
        return return_value

    @classmethod
    def read(cls,db_cursor:DBCursor,**key):
        '''
        Plugin 클래스 클래스 메소드

        ai 플러그인 db 저장소에서 특정 튜플 조회

        params
        - db_cursor : db 조작을 위한 curosor
        - key : 조회할 튜플의 모든 키값, 만약 키가 2개라면 2개의 키의 값 필요

        사용예시
        .. code-block:: python

        Plugin.read(db_cursor,sub_id=2)#키네임이 sub_id이고 찾는 튜플의 키값이 2인경우
        Plugin.read(db_cursor,status=2,id=2)#키네임이 sub_id,id이고 찾는 튜플의 키값이 2,2인경우

        '''
        cls.validate_key(key)
        table_name=cls.TableModel.__tablename__
        conditions=[]
        for i in key.items():
            conditions.append(f" {i[0]}={i[1]}")
        
        sql=f'''
        SELECT * FROM plugin.{table_name} WHERE{" and".join(conditions)};
            '''
        return_value=None
        result=db_cursor.select_sql(sql)
        if len(result):
            return_value=cls.TableModel(**result[0])
        return return_value

    @classmethod
    def create(cls,db_cursor:DBCursor,tuple):
        '''
        Plugin 클래스 클래스 메소드

        ai 플러그인 db 저장소에서 튜플 생성

        params
        - db_cursor : db 조작을 위한 curosor
        - tuple :  Plugin.TableModel 객체

        사용예시
        .. code-block:: python

        new_tuple=Plugin.TableModel(sub_id=sub_id,status=4)
        Plugin.create(db_cursor,new_wpc)

        '''
        table_name=cls.TableModel.__tablename__
        
        sql=f'''
        INSERT INTO `plugin`.`{table_name}` ({", ".join(tuple.__dict__.keys())}) VALUES ({", ".join(["%s" for i in range(len(tuple.__dict__))])});
            '''
        data=list(tuple.__dict__.values())
        db_cursor.execute_sql(sql,data)

    @classmethod
    def validate_key(cls,keys:dict=None):
        if keys:
            try:
                key_list=cls.validate_key()
                assert len(key_list)==len(keys.keys())
                for i in keys.keys():
                    assert i in key_list
                return True
            except:
                raise Exception("키값 에러")
        else:
            if type(cls.TableModel.__key__)==list:
                col_list=cls.TableModel.__annotations__
                for i in cls.TableModel.__key__:
                    assert col_list[i]==int, "키값 에러"

                return cls.TableModel.__key__
            elif type(cls.TableModel.__key__)==str:
                col_list=cls.TableModel.__annotations__
                assert col_list[cls.TableModel.__key__]==int, "키값 에러"

                return [cls.TableModel.__key__]