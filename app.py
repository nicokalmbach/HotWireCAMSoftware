from flask import Flask, render_template

import version

app = Flask(__name__)


@app.context_processor
def inject_version():
    return {"app_version": version.__version__}


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
