from flask import Flask,render_template, request
from sqlalchemy import create_engine, text, update


app = Flask(__name__)

conn_str = "mysql://root:cset155@localhost/examdb"
engine = create_engine(conn_str, echo=True)
conn = engine.connect()
# StudentTbl = conn.execute(text('select * from student')).all()
# TeacherTbl = conn.execute(text('select * from teacher')).all()



@app.route("/")
def Base():
        return render_template("Base.html")


@app.route("/Register", methods = ['GET'])
def getAccount():
    
    return render_template("Register.html")

@app.route("/Register", methods = ['POST'])
def createAccount():   
    # debugging checking if we are getting data
    data = request.form
    print(data)
    # StudentTbl = conn.execute(text('select * from student')).all()
    # TeacherTbl = conn.execute(text('select * from teacher')).all()
    # RadioValue= request.form["Teach-Stud"]
    # prevID = conn.execute(text("select Sid from student order by Sid desc Limit 1;"))
    # print(prevID)
    # print(StudentTbl)
    
    try:
        RadioValue= request.form["Teach-Stud"]
        if RadioValue == "1":
            prevID = conn.execute(text("select Sid from student order by Sid desc Limit 1;")).fetchone()
            if not prevID:
                newID = 1
            else:
                newID = int(prevID[0])+1
            
            conn.execute(text("insert into student(Sid, first_name, last_name, password) values (:Sid, :first_name, :last_name, :password)"), {"Sid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"]}
                         )
            conn.commit() 
            result = conn.execute(text('select * from student')).fetchall()
            for row in result:
                print(row)
        else:
            prevID = conn.execute(text("select Tid from teacher order by Tid desc Limit 1;")).fetchone()
            if not prevID:
                newID = 1
            else:
                newID = int(prevID[0])+1
                
            conn.execute(text("insert into teacher(Tid, first_name, last_name, password) values(:Tid, :first_name, :last_name, :password)"), {"Tid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"]})
            conn.commit()
            result = conn.execute(text('select * from teacher')).fetchall()
            
            for row in result:
                print(row)
            
        return render_template("Register.html", error = None, success = "Successfull")
    except Exception as e:
        print(f"Error: {e}")
        return render_template("Register.html", error = "Failed", success = None)

# @app.route("/Account")
# def seeAccounts():
#         return render_template("Accounts.html")

if __name__ == '__main__':
        app.run(debug=True)
    