from flask import Flask,render_template,request

app = Flask(__name__)

# examConn = 'SQL STRING'
# engine = create_engine(connectionString, echo = True)
# conn = engine.connect()


@app.route("/")
def Base():
        return render_template("Base.html")
if __name__ == '__main__':
        app.run()
    