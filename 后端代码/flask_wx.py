
# -*- coding: utf-8 -*-
import sys
from flask import Flask,render_template,request,json
import pymysql
import time
import json
import datetime
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
# json.JSONEncoder.default = lambda self, obj: (obj.isoformat() if isinstance(obj, datetime.datetime) else None)



user='scnu'
password='scd'
database='scd'
charset='utf8'


app = Flask(__name__)
@app.route('/')
def hello_world():
    return "It''s working"

# 初始界面设置
@app.route('/index',methods=['POST'])
def index():
    upload = str(json.loads(request.values.get("wxid")))
    print(upload)
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()
    
    sql="select realName,position,admitted from users where userId=%s"
    res='华南师团,default'
    try:
        res=cursor.execute(sql,upload)
        message = cursor.fetchone()
        if message[2]=='1':
            res=message[0]+','+message[1]

    except:
        # 若是没找到则添加用户
        sql = "insert into users(userId,realName,position,admitted) values(%s,'华南师团','default','1')"
        cursor.execute(sql,upload)
        
    cursor.close()
    conn.close()
    return json.dumps(res)

# 审批员工权限
@app.route('/authority',methods=['GET'])
def authority():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()

    sql="select userId, realName,position,admitted from users where admitted='0'"
    res=cursor.execute(sql)
    message = cursor.fetchall()

    cursor.close()
    conn.close()

    return json.dumps(message)


# 确认审批员工权限
@app.route('/authority_admitted',methods=['POST'])
def authority_admitted():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()
    wxid = str(json.loads(request.values.get("wxid")))
    status = str(json.loads(request.values.get("status")))
    # print(wxid)
    sql="update users set admitted=%s where userId=%s;"
    if status=='agree':
        cursor.execute(sql,['1',wxid])
        mes='已批准'
    elif status=='reject':
        cursor.execute(sql,['-1',wxid])
        mes='已拒绝'
    elif status=='clear':
        sql="update users set admitted='-1' where admitted='0';"
        cursor.execute(sql)
        mes='已拒绝全部'
    conn.commit()

    cursor.close()
    conn.close()
    return mes









# 员工管理
@app.route('/manager',methods=['GET','POST'])
def manager():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()

    sql="select userId, realName,position,admitted from users"
    res=cursor.execute(sql)
    message = cursor.fetchall()

    cursor.close()
    conn.close()

    return json.dumps(message)


# 更改员工
@app.route('/manager_change',methods=['POST'])
def manager_change():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()

    wxid = str(json.loads(request.values.get("wxid")))
    realName = str(json.loads(request.values.get("realName")))
    position = str(json.loads(request.values.get("position")))
    print(wxid,realName,position)
    sql="update users set realName=%s,position=%s,admitted=%s where userId=%s;"
    cursor.execute(sql,[realName,position,'1',wxid])
    conn.commit()
    
    
    cursor.close()
    conn.close()
    return '更改成功'







# 申请名字和职位函数
@app.route('/authorizeQueue',methods=['POST'])
def authorizeQueue():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()

    wxid = str(json.loads(request.values.get("wxid")))
    position = str(json.loads(request.values.get("position")))
    realName = str(json.loads(request.values.get("realName")))


    sql="select realName,position from users where userId=%s"
    cursor.execute(sql,wxid)
    message=cursor.fetchone()

    if message[1]=='admin':
        cursor.close()
        conn.close()
        return '不能更改管理员权限'
    
    sql="update users set realName=%s,position=%s,admitted=%s where id=%s;"
    cursor.execute(sql,[realName,position,'0',wxid])
    print(wxid,position,realName)
    cursor.close()
    conn.close()
    return 'yes'

# 查询函数
@app.route('/maps',methods=['POST'])
def maps():
    upload = str(json.loads(request.values.get("upload")))
    upload = upload.split(',')
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    if len(upload)==2:
        # 先查询商品在不在库中
        id1= upload[0]
        sql = "select * from depot where id = %s"
        res=cursor.execute(sql,[id1])
        message = cursor.fetchall()
        if not message:
            return json.dumps('商品未入库')
        # elif message[0][4]==0:
        #     return json.dumps('商品已出库')
        # elif upload_list[3]!='admin' and message[0][5]==0:
        #     return json.dumps('未允许出库')
        mes = message[0][0]+','+message[0][1]+','+str(message[0][2])+','+str(message[0][3])+','+str(message[0][4])+','+str(message[0][5])+','+message[0][6]
        print(mes)
        return mes
    else:
        print(upload)
        print(upload[1])
        id1 = upload[0]
        if(upload[1]=="类型"):
            sql = "update depot set submission_date=%s,type=%s where id=%s;"
        elif(upload[1]=="价格"):
            sql = "update depot set submission_date=%s,price=%s where id=%s;"
        elif(upload[1]=="库中"):
            sql = "update depot set submission_date=%s,status=%s where id=%s;"
        elif(upload[1]=="可出库"):
            sql = "update depot set submission_date=%s,agree_modify=%s where id=%s;"
        elif(upload[1]=="经纬度"):
            sql = "update depot set submission_date=%s,lng_lat=%s where id=%s;"
            res=cursor.execute(sql,[time.strftime("%Y%m%d"),upload[2]+','+upload[3],id1])
            conn.commit()
            cursor.close()
            conn.close()
            return '修改成功'
        print('nice')
        res=cursor.execute(sql,[time.strftime("%Y%m%d"),upload[2],id1])
        conn.commit()
        cursor.close()
        conn.close()
        return '修改成功'

# 显示所有数据
@app.route('/maps_all',methods=['GET'])
def maps_all():
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    cursor = conn.cursor()

    sql="select * from depot"
    res=cursor.execute(sql)
    message = cursor.fetchall()
    message = list(message)
    print(type(message))
    for i in range(len(message)):
        message[i]=list(message[i])
        message[i][3]=str(message[i][3])
    print(message)
    

    cursor.close()
    conn.close()

    return json.dumps(message)


# 入库函数
@app.route('/send',methods=['POST'])
def send():
    upload = str(json.loads(request.values.get("upload")))
    upload_list = upload.split(',')
    if len(upload_list)!=6:
        return json.dumps('错误二维码')
    lng_lat = upload_list[4] +','+ upload_list[5] # 经纬度
    # print(upload_list)
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    sql = "insert into depot(id,type,price,submission_date,lng_lat) values(%s,%s,%s,%s,%s);"
    # 执行SQL语句
    id1,type1,price,submission_date = upload_list[0],upload_list[1],upload_list[2],time.strftime("%Y%m%d")  # 'AA3002059','C',203.5,time.strftime("%Y%m%d")
    try:
        res=cursor.execute(sql,[id1,type1,price,submission_date,lng_lat])
        # 涉及写操作要注意提交
        conn.commit()
    except pymysql.err.IntegrityError:
        sql="select status from depot where id=%s"
        cursor.execute(sql,[upload_list[0]])
        message = cursor.fetchone()[0]
        if message==0:
            if upload_list[3]=='admin':
                sql = "update depot set status=1,submission_date=%s,lng_lat=%s,agree_modify='0' where id=%s;"
                cursor.execute(sql,[time.strftime("%Y%m%d"),lng_lat,upload_list[0]])
                conn.commit()
                return json.dumps('重新入库成功')
            else:
                return json.dumps('无权限重新入库')
        return json.dumps('数据重复')
    finally:
        # 关闭光标对象
        cursor.close()
        # 关闭数据库连接
        conn.close()
    if res==1:
        # print res
        return json.dumps('数据提交成功')
    else:
        return json.dumps('数据提交失败')

# 出库函数
@app.route('/delete',methods=['POST'])
def delete():
    upload = str(json.loads(request.values.get("upload")))
    upload_list = upload.split(',')
    if len(upload_list)!=6:
        return json.dumps('错误二维码')
    print(upload_list)
    lng_lat = upload_list[4] +','+ upload_list[5] # 经纬度
    conn = pymysql.connect(host='127.0.0.1', user=user,password=password,database=database,charset=charset)
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 先查询商品在不在库中
    id1= upload_list[0]
    sql = "select * from depot where id = %s"
    res=cursor.execute(sql,[id1])
    message = cursor.fetchall()
    if not message:
        return json.dumps('商品未入库')
    elif message[0][4]==0:
        return json.dumps('商品已出库')
    elif upload_list[3]!='admin' and message[0][5]==0:
        return json.dumps('未允许出库')

    # 将status置为0表示出库
    # 定义要执行的SQL语句
    sql = "update depot set status=0,submission_date=%s,lng_lat=%s where id=%s;"
    try:
        res=cursor.execute(sql,[time.strftime("%Y%m%d"),lng_lat,id1])
        message = cursor.fetchall()
        # 涉及写操作要注意提交
        conn.commit()
    finally:
        # 关闭光标对象
        cursor.close()
        # 关闭数据库连接
        conn.close()
    if res==1:
        return json.dumps('出库成功')
    else:
        return json.dumps(res)
    return json.dumps('商品未入库或已出库')

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=80)
