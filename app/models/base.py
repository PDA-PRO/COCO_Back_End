class ModelBase():
    def __init__(self,**args) -> None:
        for i in self.__annotations__.items():
            if isinstance( args.get(i[0]),(i[1]|None)):
                self.__setattr__(i[0],args.get(i[0]))
            else:
                raise TypeError(f"{i[0]} 의 타입은 {i[1]}로 예상되지만 실제 타입은 {type(args.get(i[0]))}입니다")