from flask import Flask,render_template
from flask_mysqldb import MySQL
from pymysql import*
from sqlalchemy.dialects.mysql import BIGINT
from flask import request,redirect, url_for
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import insert
import pandas as pd


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ppe'

db = MySQL(app)

@app.route("/")
def index():
    return render_template('ppe.html')

@app.route("/return")
def returns():
    return render_template('return.html')

@app.route("/result")
def result():
    return render_template('result.html')

@app.route("/logs", methods = ['POST'])
def logs():
    if request.method == 'POST':
        empID = request.form['empID']
        ppeID = request.form['ppeID']
        now = datetime.now()

        #Cursor connection
        selcursor = db.connection.cursor()
        selcursor.execute(''' SELECT status FROM ppe WHERE ppe_id=%s ''', [ppeID])
        ppeStatus = selcursor.fetchall()
        db.connection.commit()
        selcursor.close()

        latestcursor = db.connection.cursor()
        latestcursor.execute(''' SELECT * FROM logs WHERE ppe_id=%s ORDER BY log_id DESC''', [ppeID])
        latestLog = latestcursor.fetchall()
        db.connection.commit()
        selcursor.close()

        print(int(ppeStatus[0][0]))
        print(latestLog)
        if ppeStatus[0][0] == 0: 
            if str(latestLog[0][2]) == str(empID):
                cursor = db.connection.cursor()
                cursor.execute(''' REPLACE INTO ppe (ppe_id, status) VALUES (%s, 1) ''', [ppeID])
                cursor.execute(''' INSERT INTO logs (ppe_id,employee_id,loan_datetime,return_datetime) VALUES(%s,%s,%s,%s)''',(ppeID,empID,now,None))
                db.connection.commit()
                cursor.close()
            else:
                print('error: suit already loaned out')
        if ppeStatus[0][0] == 1: 
            if str(latestLog[0][2]) == str(empID):
                cursor = db.connection.cursor()
                cursor.execute(''' REPLACE INTO ppe (ppe_id, status) VALUES (%s, 0) ''', [ppeID])
                cursor.execute(''' UPDATE logs SET return_datetime=%s WHERE log_id=%s ''',(now, [latestLog[0][0]]))
                db.connection.commit()
                cursor.close()
            else:
                print('error: suit already loaned out')

    return render_template('ppe.html')

@app.route("/records")
def records():
    con=connect(user="root",password="",host="localhost",database="ppe")
    with pd.ExcelWriter('ppe_records.xlsx') as writer:
        df=pd.read_sql('select * from employees', con)
        df.to_excel(writer, sheet_name="emp")

        df=pd.read_sql('select * from ppe', con)
        df.to_excel(writer, sheet_name="ppe")
        
        df=pd.read_sql('SELECT * FROM logs WHERE return_datetime IS NOT NULL', con)
        df.to_excel(writer, sheet_name="logs")

    return render_template('ppe.html')

if __name__ == "__main__":
    app.run(debug=True)