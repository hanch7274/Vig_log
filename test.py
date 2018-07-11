import pymysql
import re
#연속된 로그에서 로그 하나를 추출하는 정규표현식
p = re.compile('\d+-\d+-\d+.+dst_port=\d+')
# pymysql모듈을 이용하여 mysql 로그인
db = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='root',db='log',charset='utf8')
#db조작에 필요한 cursor객체 생성
cursor = db.cursor()
#로그파일 binary타입으로 open
r = open("G:\\firewall.log","rb")
#넣은 로그 개수를 세기 위한 변수
input_num = 0;
#아래서부터 일정 크기(140h)만큼 읽어와서 정규표현식을 사용하여 데이터를 추출하고, 문자를 슬라이싱하여 리스트에 저장한다.
while True:
    r_data = r.read(0x140)
    if not r_data:
        print("road finished")
        break
    else:
        try:
            reg_data = p.findall((str(r_data)))
            reg_len = len(r_data)-len(reg_data[0])
            data = re.split('[= ]',reg_data[0])
            data[0] = data[0]+data[1]
            #이 과정에서 날짜데이터의 ':', '-' 문자는 모두 없어진다.
            data[0] = data[0].replace('-','').replace(':','')
            data.pop(1)
        except:
            pass
        sql = '''INSERT INTO fw_log
(log_time,src_mac,dst_mac,src_ip,dst_ip,len,src_port,dst_port)
VALUES(%s,%s,%s,INET_ATON(%s),INET_ATON(%s),%s,%s,%s)'''
        try:
            cursor.execute(sql,(data[0],data[18],data[20],data[22],data[24],data[26],data[28],data[30]))
            input_num +=1
            #read()함수 호출에 따른 포인터값을 seek()로 조정해준다.
            r.seek(-(reg_len-1),1)
            if(input_num%10000==1):
                print(input_num)
                #데이터 부하를 줄이기 위해 10000개 단위로 commit을 진행한다.
                db.commit()
        except:
            r.seek(-(reg_len-1),1)
            continue

print("finished  input_num:{}".format(input_num))

