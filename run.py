from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت والموقع يعملان بنجاح! 🎉"

@app.route('/matches')
def matches():
    return "📋 قائمة المباريات: سيتم إضافتها قريباً"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
