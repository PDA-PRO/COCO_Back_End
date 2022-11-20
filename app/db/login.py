import query
# 디비 확인 -> 일치 여부 검사


def check_db(user):
    sql1 = f"SELECT id, pw FROM `coco`.`coco_student` where id = '{user.id}';"
    sq12 = f"SELECT id, pw FROM `coco`.`coco_teacher` where id = '{user.id}';"
    result1 = query.execute_mysql(sql1)
    result2 = query.execute_mysql(sq12)
    if len(result1) == 0 and len(result2) == 0:
        return 0
    else:
        if user.pw == result1[0][1] or user.pw == result2[0][1]:
            return 1
        return 0


# 새로운 회원 정보 insert
def insert_db(user):
    sql = f"INSERT INTO `coco`.`coco_student` (`name`, `id`, `pw`) VALUES ('{user.name}', '{user.id}', '{user.pw}');"
    if user.type != 1:
        sql = f"INSERT INTO `coco`.`coco_teacher` (`name`, `id`, `pw`) VALUES ('{user.name}', '{user.id}', '{user.pw}');"
    query.insert_mysql(sql)
    # con = pymysql.connect(host='localhost', user='root', password='qwer1234',
    #                    db='coco', charset='utf8') # 한글처리 (charset = 'utf8')
    # cur = con.cursor()
    # cur.execute(sql)
    # con.commit()
    # con.close()
    return 1


# 회원가입시 아이디 중복 검사
def find_ids(id):
    sql1 = f"SELECT id FROM `coco`.`coco_student` where id = '{id}';"
    sq12 = f"SELECT id FROM `coco`.`coco_teacher` where id = '{id}';"
    result1 = query.execute_mysql(sql1)
    result2 = query.execute_mysql(sq12)
    if len(result1) == 0 and len(result2) == 0:
        return 1
    else:
        return 0
