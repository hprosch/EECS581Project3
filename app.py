from flask import Flask, render_template

# create flask application, and stores it to 'app' variable
app = Flask(__name__)

#defines what happens when someone visits home page
@app.route("/")

#function represents home page
def home():
    # loads HTML file from templates/
    return render_template("index.html")

if __name__ == "__main__":
    # starts flask with development debugging enabled
    app.run(debug=True)
