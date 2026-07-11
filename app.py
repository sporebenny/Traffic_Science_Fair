
#print("hello world ")

#test flask 
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Traffic Science Fair System"


if __name__ == "__main__":
    app.run(debug=True)