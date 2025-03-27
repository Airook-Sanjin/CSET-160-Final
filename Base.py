from flask import Flask,render_template, request
from sqlalchemy import create_engine, text, update


app = Flask(__name__)

conn_str = "mysql://root:cset155@localhost/examdb" # connects to DataBase
engine = create_engine(conn_str, echo=True)
conn = engine.connect()


@app.route("/Home")
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
    
    try:
        RadioValue= request.form["Teach-Stud"]
        if RadioValue == "1": #Checks whether Student or Teacher was clicked
            prevID = conn.execute(text("select Sid from student order by Sid desc Limit 1;")).fetchone() #Grabs last ID from Student table
            if not prevID:
                newID = 1
            else:
                newID = int(prevID[0])+1
            
            conn.execute(text("insert into student(Sid, first_name, last_name, password) values (:Sid, :first_name, :last_name, :password)"), {"Sid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"]}
                         )
            conn.commit() 
            result = conn.execute(text('select * from student')).fetchall() #For Debugging
            for row in result:
                print(row)
        else:
            prevID = conn.execute(text("select Tid from teacher order by Tid desc Limit 1;")).fetchone() #Grabs last ID from Teacher table
            if not prevID: #if There is no ID, newID is 1
                newID = 1
            else:
                newID = int(prevID[0])+1 #increments 1 from prevID
                
            conn.execute(text("insert into teacher(Tid, first_name, last_name, password) values(:Tid, :first_name, :last_name, :password)"), {"Tid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"]})
            
            conn.commit()
            
            result = conn.execute(text('select * from teacher')).fetchall()
            
            for row in result:
                print(row)
            
        return render_template("Register.html", error = None, success = "Successfull")
    except Exception as e:
        print(f"Error: {e}") 
        return render_template("Register.html", error = "Failed", success = None)


@app.route("/Account", methods = ['GET'] )
def seeAccounts():
    StudentTBL = conn.execute(text('select * from student')).fetchall()
    TeacherTBL = conn.execute(text('select * from teacher')).fetchall()
    return render_template("Accounts.html",StudentTBL = StudentTBL,TeacherTBL = TeacherTBL )

@app.route("/Account", methods = ['POST'] )
def SearchAccounts():
    SpecificStudent = None # Set to None for it to work properly on HTML
    TeacherTBL = None # Set to None for it to work properly on HTML
    try:
        
        RadioValue = request.form.get("Teach-Stud")
        print(f"Radio: {RadioValue}")
        
        
        if RadioValue == "1":  # check if any radio button is clicked. If Student selected, it will show only student Table
            SpecificStudent = conn.execute(text("Select * from student Where first_name = :first_name or last_name = :first_name or Concat(first_name,' ',last_name) = :first_name"),request.form ).fetchall() # searches for specific student 
            if SpecificStudent == []: #If user is not found it will be error
                return render_template("Accounts.html", error = "Student Not Found", success = None)
            print(f"Student Result: {SpecificStudent}")
        
        else: # check if any radio button is clicked. Else, it will show only teacher Table
            
            TeacherTBL = conn.execute(text("Select * from teacher Where first_name = :first_name or last_name = :first_name or Concat(first_name,' ',last_name) = :first_name"),request.form ).fetchall() # searches for specific teacher name 
            if TeacherTBL == []: #If user is not found it will be error
                return render_template("Accounts.html", error = "Teacher Not Found", success = None)
            print(f"Teacher Result: {TeacherTBL}")
            
        return render_template("Accounts.html",StudentTBL = SpecificStudent if SpecificStudent else [],TeacherTBL = TeacherTBL if TeacherTBL else [] ,error = None, success = "Successfull" )
    except Exception as e:
        print(f"Error: {e}") 
        return render_template("Accounts.html", error = "User Not Found", success = None)


@app.route("/MakeTest", methods = ['GET'] )
def getTest():
    return render_template("MakeTest.html")

@app.route("/MakeTest", methods = ['POST'] )
def createTest():
    try:
        conn.execute(text("""INSERT INTO Exam (TestID, Grade, StudentID, TeacherID) 
                                VALUES (:testid, NULL, NULL, :teacherid)
                        """), request.form)
        conn.execute(text("""INSERT INTO Questions (QuestionsID, TestID, question, answer) 
                                 VALUES (:qid, :testid, :quest, :ans)
                        """), request.form)
        conn.commit() # to add to the database
        return render_template('MakeTest.html', error = None, success = "Successfull")
    except Exception as e:
        print(f"Failed: {e}")
        return render_template('MakeTest.html', error=f"Failed: {e}", success=None)
    
    

if __name__ == '__main__':
        app.run(debug=True)
    