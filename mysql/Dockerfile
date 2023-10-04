FROM mysql:8.0.32

#db 초기화에 필요한 스크립트 복사
ADD ./db/ /docker-entrypoint-initdb.d/

#db 설정값 복사
ADD ./conf.d /etc/mysql/conf.d

EXPOSE 3306

CMD ["mysqld"]
