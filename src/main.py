from flask import Flask

app = Flask(__name__)

@app.route("/status")
def status():
    return "Status is OK, ready to receive data."

if __name__ == "__main__":
    app.run()