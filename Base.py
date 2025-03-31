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
        
    if "User" in session:
        g.User = session["User"]
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
        User={}
        if conn.execute(text("Select Email From student Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone(): #Checks if ValidUser is in DB-Student Table 
            User["Name"] = conn.execute(text("Select first_name From student Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0] #grabs first_name from DB-Student Table
            User["ID"] = conn.execute(text("Select Sid From student Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0]
            Student=True 
            print(User["Name"])
        else: # if ValidUser is not in DB-Student Table
            Student=False
            User["Name"] = conn.execute(text("Select first_name From teacher Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0] #grabs first_name from DB-Teacher Table
            User["ID"] = conn.execute(text("Select tid From teacher Where Email in(:Email)"),{"Email": ValidUser[0][0]}).fetchone()[0]
            print(User["Name"])
        session["Student"] = Student # Storing Student in SessionStorage to see across mutliple requests
        g.Student=Student # Makes Student availabe on current request for template
        session["User"] = User # Storing User in SessionStorage to see across mutliple requests
        g.User = User # Makes UserName availabe on current request for template
        print(g.User["Name"])
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
                SELECT e.TestName, t.tid, t.last_name, COUNT(DISTINCT q.QuestionsID) as TotalQuestions,e.TestID, g.grade,Case When g.Grade is Not NULL Then True else False end as TestTaken
                FROM questions AS q 
                JOIN exam AS e ON q.testid = e.testId 
                JOIN teacher AS t ON e.teacherid = t.tid
                left Join grade as g on g.TestID = e.testid
                Group By e.TestID,e.TestName,t.last_name,g.grade;""")).fetchall()
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
    g.User = session["User"]
    
    
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
    Score = 0
    try:
        for QNumber in ListofQuestionID:
            Result = conn.execute(text("""
            Select e.Testid, Count(q.Question) as TotalQuestions, Cast(sum( Case When q.answer = :Answer Then 1 else 0 end) as Unsigned) as AnsweredCorrectly
            FROM questions AS q 
            JOIN exam AS e ON q.testid = e.testId
            Where e.testid = :TestID and q.questionsID = :questionID
            Group by e.testid"""),{"TestID": g.TestID, "Answer": request.form[f"Answer{QNumber[0]}"],"questionID":QNumber[0]}).fetchone() # Cast() makes sure q.answer is a INT - Unsigned means that It won't be a negative
            
            print(f"ANSWER : {request.form[f'Answer{QNumber[0]}']}") # FOR DEBUGGIN
            print(f"RESULT : {Result}") # FOR DEBUGGIN
            if Result[2]==1: # Checks if q.answer is one if so it will increment Score by 1
                Score+=1
        Score = round((Score/ len(TestInfo)) *100) # Turns Score into percentage
        conn.execute(text("""
        INSERT INTO grade
	        (TestID,grade,StudentID)
        Values
	        (:TestID,:Result,:StudentID);
"""),{"TestID":g.TestID, "Result":Score,"StudentID":g.User["ID"]})
        conn.commit()
        testComplete = True # Marks Test as complete
        
        return render_template("TakeTest.html", error = None, success="Submission Successful", Test = TestInfo, Result = Score, TestComplete = testComplete)
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

        test_id = request.form["testid"]
        teacher_id = request.form["teacherid"]
        testname = request.form["Testname"]
        
        # Step 1: Validate TestID exists in Exam table and matches TeacherID
        validation_query = text("""
            SELECT TeacherID
            FROM Exam
            WHERE TestID = :testid
        """)
        existing_exam = conn.execute(validation_query, {"testid": test_id}).fetchone()

        if existing_exam:
            if str(existing_exam[0]) != str(teacher_id):
                # Debug: Log mismatch
                print(f"Validation failed: TestID {test_id} is not associated with TeacherID {teacher_id}.")
                return render_template('MakeTest.html', error="Mismatch between TestID and TeacherID.", success=None)
        else:
            # If TestID doesn't exist, create it
            if not teacher_id:
                return render_template('MakeTest.html', error="TeacherID is required to create a new test.", success=None)

            # Insert new TestID into Exam table
            conn.execute(text("""
                INSERT INTO Exam (TestName,TestID, TeacherID) 
                VALUES (:Testname,:testid, :teacherid)
            """), {"testid": test_id, "teacherid": teacher_id, "Testname": testname})

        # Step 2: Validate TeacherID exists
        existing_teacher = conn.execute(text("""
            SELECT * 
            FROM Teacher 
            WHERE Tid = :teacherid
        """), {"teacherid": teacher_id}).fetchone()
        if not existing_teacher:
            return render_template('MakeTest.html', error="TeacherID not found.", success=None)

        # Step 3: Get next QuestionsID dynamically
        question_result = conn.execute(text("""
            SELECT MAX(QuestionsID) AS max_qid 
            FROM Questions
        """))
        next_qid = question_result.fetchone()[0]
        if next_qid is None:
            next_qid = 1
        else:
            next_qid += 1

        # Step 4: Insert into Questions table
        conn.execute(text("""
            INSERT INTO Questions (QuestionsID, TestID, question, answer) 
            VALUES (:qid, :testid, :quest, :ans)
        """), {"qid": next_qid, "testid": test_id, "quest": request.form["quest"], "ans": request.form["ans"]})

        # Commit changes and fetch updated questions list
        questions = conn.execute(text("""
            SELECT e.TestName, e.TestID,q.answer, q.question,q.questionsID,e.TeacherID
            FROM questions AS q 
            JOIN exam AS e ON q.testid = e.testId
            Where e.TestID = :testid
        """), {"testid": test_id}).all()
        conn.commit()
        return render_template('MakeTest.html', error=None, success="Successfully added the question to the test!", questions=questions)

    except Exception as e:
        print(f"Insertion Error: {e}")
        return render_template('MakeTest.html', error=f"Failed: {e}", success=None, questions=[])

# -----------------------
# --- DELETE QUESTION ---
# -----------------------
@app.route("/DeleteTest", methods=['GET'])
def getTestQ():
    return render_template("DeleteTest.html", worked=None, nowork=None)

@app.route("/DeleteTest", methods=['POST'])
def deleteTest():
    try:
        test_id = request.form["testid"]
        teacher_id = request.form["teacherid"]

        # Debug: Print input values
        print(f"Received TestID: {test_id}, TeacherID: {teacher_id}")

        # Step 1: Validate the existence of TestID and TeacherID pair
        validation_query = text("""
            SELECT COUNT(*) AS count
            FROM Exam
            WHERE TestID = :testid AND TeacherID = :teacherid
        """)
        result = conn.execute(validation_query, {"testid": test_id, "teacherid": teacher_id}).fetchone()

        # Access the count value using the correct index
        count = result[0]  # Access the first element of the tuple

        if count == 0:
            # Debug: Log mismatch
            print("Validation failed: TestID and TeacherID do not match.")
            return render_template("DeleteTest.html", worked=None, nowork="Invalid TestID or TeacherID pair.")

        # Step 2: Delete related rows in Questions
        delete_questions_query = text("""
            DELETE FROM Questions
            WHERE TestID = :testid
        """)
        conn.execute(delete_questions_query, {"testid": test_id})

        # Step 3: Delete the TestID in Exam
        delete_exam_query = text("""
            DELETE FROM Exam
            WHERE TestID = :testid AND TeacherID = :teacherid
        """)
        conn.execute(delete_exam_query, {"testid": test_id, "teacherid": teacher_id})

        conn.commit()  # Commit the changes
        return render_template("DeleteTest.html", worked="Test and associated questions successfully deleted.", nowork=None)

    except Exception as e:
        # Debug: Log the exception
        print(f"Error during DELETE operation: {e}")
        return render_template("DeleteTest.html", worked=None, nowork="An error occurred while deleting the Test.")

    
# -----------------------
# --- SEARCH TEST -------
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
    