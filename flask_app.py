from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route("/star-cafe-menu")
def menu():
    return render_template("cafe-menu.html")

@app.route("/shipra")
def shipra():
    return render_template("shipra.html")

if __name__ == "__main__":
    app.run(debug=True)