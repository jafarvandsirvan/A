from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask!"

if __name__ == "__main__":
    # تغییر پورت به 5001
    app.run(debug=True, host="0.0.0.0", port=5001)
