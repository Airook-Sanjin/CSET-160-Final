from flask import Flask,render_template, request, g, session
from sqlalchemy import create_engine, text, update
import secrets 

app = Flask(__name__)
app.secret_key = secrets.token_hex(15) # Generates and sets A secret Key for session with the secrets module

conn_str = "mysql://root:cset155@localhost/examdb" # connects to DataBase
engine = create_engine(conn_str, echo=True)
conn = engine.connect()
# ----------------------Before each load------------------------------------
@app.before_request # Before each request it will look for the values below
def load_user():
    if "TestID" in session:
        g.TestID = session["TestID"]
    else:
        g.TestID = None
    if "Student" in session:
        g.Student = session["Student"]
    else:
        g.Student = None
    if "UserName" in session:
        g.UserName = session["UserName"]
    else:
        g.UserName = None
# --------Main------------------------------

@app.route("/", methods = ["GET"])
def Base():
    
    return render_template("Login.html")

@app.route("/", methods = ["POST"])

def LogIn():
    try:
        ValidUser = (conn.execute(text("select Email, password from student Where Email = :Email"),request.form ).fetchall() + conn.execute(text("select Email, password from teacher Where Email = :Email"),request.form ).fetchall())
    
        if conn.execute(text("Select Email From student Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone(): #Checks if ValidUser is in DB-Student Table 
            UserName = conn.execute(text("Select first_name From student Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0] #grabs first_name from DB-Student Table
            Student=True 
        else: # if ValidUser is not in DB-Student Table
            Student=False
            UserName = conn.execute(text("Select first_name From teacher Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0] #grabs first_name from DB-Teacher Table

        session["Student"] = Student # Storing Student in SessionStorage to see across mutliple requests
        g.Student=Student # Makes Student availabe on current request for template
        session["UserName"] = UserName # Storing Username in SessionStorage to see across mutliple requests
        g.UserName = UserName # Makes UserName availabe on current request for template
        
        return render_template("Home.html") 
    except Exception as e:
        print(f"Error: {e}") 
        return render_template("Login.html", error = "User or password is not correct", success = None)
    
#------------HOMEPAGE---------------
@app.route("/Home")
def ViewHome():
    
    return render_template("Home.html")

@app.route("/Register", methods = ['GET'])
def getAccount():
    
    return render_template("Register.html")

#--------SIGN UP----------------

@app.route("/Register", methods = ['POST'])
def createAccount():   
    # debugging checking if we are getting data
    data = request.form
    print(data)
    
    try:
        RadioValue= request.form["Teach-Stud"]
        if RadioValue == "1": #Checks whether Student or Teacher was clicked
            prevID = conn.execute(text("select Sid from student order by Sid desc Limit 1;")).fetchone() #Grabs last ID from Student table
            if not prevID: # If There is no prevID, newID is 1
                newID = 1
            else:
                newID = int(prevID[0])+1 # Increments 1 from prevID
            
            conn.execute(text("insert into student(Sid, first_name, last_name, password, Email) values (:Sid, :first_name, :last_name, :password, :Email)"), {"Sid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"],"Email":request.form["Email"]}
                         )
            conn.commit() 
            
            result = conn.execute(text('select * from student')).fetchall() #For Debugging
            
            for row in result:
                print(row)
        else:
            prevID = conn.execute(text("select Tid from teacher order by Tid desc Limit 1;")).fetchone() #Grabs last ID from Teacher table
            if not prevID: # If There is no prevID, newID is 1
                newID = 1
            else:
                newID = int(prevID[0])+1 # Increments 1 from prevID
                
            conn.execute(text("insert into teacher(Tid, first_name, last_name, password, Email) values(:Tid, :first_name, :last_name, :password, :Email)"), {"Tid": newID, "first_name":request.form["first_name"], "last_name":request.form["last_name"],"password":request.form["password"], "Email":request.form["Email"]})
            
            conn.commit()
            
            result = conn.execute(text('select * from teacher')).fetchall()
            
            for row in result:
                print(row)
            
        return render_template("Register.html", error = None, success = "Successfull")
    except Exception as e:
        print(f"Error: {e}") 
        return render_template("Register.html", error = "Failed", success = None)

# ----VIEW ACCOUNT PAGE -------------
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
# -------View ALL TESTS----------------
@app.route("/ViewTest")
def ViewAllTest(): 
    try:
        AllTests = conn.execute(text("""
                SELECT e.TestName, t.tid, t.last_name, COUNT(DISTINCT q.QuestionsID) as TotalQuestions
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.testId 
                JOIN teacher AS t ON e.teacherid = t.tid Group By e.TestID,e.TestName,t.last_name;""")).fetchall()
        print(AllTests)
        return render_template("ViewTest.html", error = None, success = "TestsFound",AllTests = AllTests)
    except:
        return render_template("ViewTest.html",error = "User Not Found", success = None, AllTests = AllTests)


    
#  --------------Take Test-----------
@app.route("/TakeTest", methods=["GET"])
def TestTaking():
    TestID = request.args.get("TestID") #Grabs argument from ViewTest
    
    session["TestID"] = TestID # Storing TestID in SessionStorage to JUST so I can see it in the POST - THere must be a better way
    g.TestID=TestID # Makes TestID availabe on current request for template
    print(f"GET: {TestID}") # FOR DEBUGGIN
    try:
        TestInfo = conn.execute(text(""" 
                SELECT e.TestName, e.TestID,q.answer, q.question,q.questionsID
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.TestID 
                WHERE e.testID = :TestID"""),{"TestID":TestID}).fetchall() # Joins and Grabs Tables-Exam and questions 
        print(f"TestINFO GET : {TestInfo}") # FOR DEBUGGIN
        return render_template("TakeTest.html", error = None, success="TestID Found", Test = TestInfo)
    except: 
        return render_template("TakeTest.html", error = "Test ID invalid", success=None, Test = TestInfo)
@app.route("/TakeTest", methods=["POST"])
def SubmitTest():
    g.TestID = session["TestID"]
    
    TestInfo = conn.execute(text(""" 
                SELECT e.TestName, e.TestID,q.answer, q.question,q.questionsID
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.TestID 
                WHERE e.testID = :TestID"""),{"TestID":g.TestID}).fetchall()
    
    ListofQuestionID = conn.execute(text(""" 
                SELECT q.questionsID
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.TestID 
                WHERE e.testID = :TestID"""),{"TestID":g.TestID}).fetchall()
    print(f"LOQ :{ListofQuestionID}")
    
    print(f"TestINFO POST : {TestInfo}") # FOR DEBUGGIN
    Score=0
    try:
        for QNumber in ListofQuestionID:
            Result = conn.execute(text("""
            Select e.Testid, Count(q.Question) as TotalQuestions, Cast(sum( Case When q.answer = :Answer Then 1 else 0 end) as Unsigned) as AnsweredCorrectly
            FROM questions AS q 
            JOIN exam AS e ON q.testid = e.testId
            Where e.testid = :TestID and q.questionsID = :questionID
            Group by e.testid"""),{"TestID": g.TestID, "Answer": request.form[f"Answer{QNumber[0]}"],"questionID":QNumber[0]}).fetchone()
            print(f"ANSWER : {request.form[f'Answer{QNumber[0]}']}") # FOR DEBUGGIN
            print(f"RESULT : {Result}") # FOR DEBUGGIN
            if Result[2]==1:
                Score+=1
        print(int(Score/ len(TestInfo) *100)) # FOR DEBUGGIN
        testComplete = True
        
        return render_template("TakeTest.html", error = None, success="Submission Successful", Test = TestInfo, Result = int(Score/ len(TestInfo) *100), TestComplete = testComplete)
    except:
        return render_template("TakeTest.html", error = "Failed", success=None, TestComplete=None)
#--------MAKE TEST PAGE----------

@app.route("/MakeTest", methods = ['GET'] )
def getTest():
    questions = []
    return render_template("MakeTest.html", questions=questions)

@app.route("/MakeTest", methods=['POST'])
def createTest():
    try:
        print("Form Data:", request.form)

        # Check if TestID exists in the Exam table
        existing_exam = conn.execute(text("SELECT * FROM Exam WHERE TestID = :testid"), {"testid": request.form["testid"]}).fetchone()
        if not existing_exam:
            # Create a new TestID in Exam table
            teacherid = request.form.get("teacherid")
            if not teacherid:
                return render_template('MakeTest.html', error="TeacherID is required to create a new test.", success=None)
            
            # Insert new TestID into Exam table
            conn.execute(text("""
                INSERT INTO Exam (TestID, Grade, StudentID, TeacherID) 
                VALUES (:testid, NULL, NULL, :teacherid)
            """), {
                "testid": request.form["testid"],
                "teacherid": teacherid
            })

        # Validate if TeacherID exists
        existing_teacher = conn.execute(text("SELECT * FROM Teacher WHERE Tid = :teacherid"), {"teacherid": request.form["teacherid"]}).fetchone()
        if not existing_teacher:
            return render_template('MakeTest.html', error="TeacherID not found.", success=None)

        # Get next QuestionsID dynamically
        question_result = conn.execute(text("SELECT MAX(QuestionsID) AS max_qid FROM Questions"))
        next_qid = question_result.fetchone()[0]  # Get the highest QuestionsID
        if next_qid is None:
            next_qid = 1  # Start from 1 if no records exist
        else:
            next_qid += 1  # Increment QuestionsID for the new question

        # Insert into Questions table with dynamically generated QuestionsID
        conn.execute(text("""
            INSERT INTO Questions (QuestionsID, TestID, question, answer) 
            VALUES (:qid, :testid, :quest, :ans)
        """), {
            "qid": next_qid,
            "testid": request.form["testid"],
            "quest": request.form["quest"],
            "ans": request.form["ans"]
        })

        # Commit changes
        questions = conn.execute(text("select q.*, t.tid, t.first_name, t.last_name from questions as q join exam as e on q.testid = e.testId join teacher as t where (e.teacherid = t.tid and q.questionsid) and e.Testid = :testid"), {"testid": request.form["testid"]}).all()
        conn.commit()
        return render_template('MakeTest.html', error=None, success="Successfully added the question to the test!", questions=questions)
    except Exception as e:
        print(f"Insertion Error: {e}")
        return render_template('MakeTest.html', error=f"Failed: {e}", success=None, questions=questions)

# -----------------------
# --- DELETE QUESTION ---
# -----------------------
@app.route("/DeleteTest", methods=['GET'])
def getTestQ():
    return render_template("DeleteTest.html", worked=None, nowork=None)

@app.route("/DeleteTest", methods=['POST'])
def deleteTest():
    try:
        # Step 1: Delete related rows in Questions
        conn.execute(text("""
            DELETE FROM Questions
            WHERE TestID = :testid
        """), {"testid": request.form["testid"]})

        # Step 2: Delete the TestID in Exam
        conn.execute(text("""
            DELETE FROM Exam
            WHERE Testid = :testid AND TeacherID = :teacherid
        """), {"testid": request.form["testid"], "teacherid": request.form["teacherid"]})

        conn.commit()  # Commit the changes
        return render_template("DeleteTest.html", worked="Test and associated questions successfully deleted.", nowork=None)
    except Exception as e:
        print(f"Error during DELETE operation: {e}")  # Log the error for debugging
        return render_template("DeleteTest.html", worked=None, nowork="An error occurred while deleting the Test.")

    
# -----------------------
# --- SEARCH TEST ---
# -----------------------  
@app.route("/SearchTest", methods = ['GET'] )
def recieveQuest():
    Test = []
    return render_template("DeleteTest.html", Test=Test)

@app.route("/SearchTest", methods=['POST']) 
def SearchQuest():
    try:
        # Query to find the existing TestID
        page = request.form.get("page", "DeleteTest")
        existing_testID = conn.execute(text("""
            SELECT q.*, t.tid, t.first_name, t.last_name 
            FROM questions AS q 
            JOIN exam AS e ON q.testid = e.testId 
            JOIN teacher AS t ON e.teacherid = t.tid 
            WHERE e.Testid = :testid
        """), {"testid": request.form["testid"]}).all()

        if existing_testID and len(existing_testID) > 0:  # If TestID exists, return associated questions
            return render_template(f"{page}.html", error=None, success="TestID Found", Test=existing_testID)
        else:  # If TestID doesn't exist
            return render_template(f"{page}.html", error="Test ID does not exist.", success=None, Test=None)
    except Exception as e:
        print(f"Error: {e}")  # Log the actual exception
        return render_template(f"{page}.html", error="An error occurred while processing your request.", success=None, Test=None)


# -------------------
# -----EDIT TEST-----
# -------------------

@app.route("/EditTest", methods=['GET'])
def getEdit():
    return render_template("EditTest.html", worked=None, nowork=None)

@app.route("/EditTest", methods=['POST'])
def EditTest():
    testid = request.form.get("testid")
    teacherid = request.form.get("teacherid")
    quest = request.form.get("quest")
    ans = request.form.get("ans")
    QID = request.form.get("QID")

    # Check if the test exists and belongs to the teacher
    check = conn.execute(
        text("SELECT * FROM exam WHERE Testid = :testid AND teacherid = :teacherid"),
        {"testid": testid, "teacherid": teacherid}
    ).fetchone()

    if check:  # If a matching record is found
        conn.execute(
            text("UPDATE questions SET question = :quest, answer = :ans WHERE QuestionsID = :QID"),
            {"quest": quest, "ans": ans, "QID": QID}
        )
        conn.commit()

        # Retrieve the updated data after making changes
        Test = conn.execute(
            text("""
                SELECT q.*, t.tid, t.first_name, t.last_name 
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.testId 
                JOIN teacher AS t ON e.teacherid = t.tid 
                WHERE e.Testid = :testid
            """),
            {"testid": testid}
        ).fetchall()

        return render_template("EditTest.html", worked="Test updated successfully!", nowork=None, Test=Test)

    else:
        return render_template("EditTest.html", worked=None, nowork="You're not authorized. This is not your test. Make a new one.", Test=[])


if __name__ == '__main__':
        app.run(debug=True)
    