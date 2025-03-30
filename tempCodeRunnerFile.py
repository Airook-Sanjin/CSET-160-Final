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
        return render_template("TakeTest.html", error = "Test ID inva