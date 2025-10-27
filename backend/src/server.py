from .app import create_app

flask_app = create_app()

@flask_app.route("/")
def hello():
    return "hello world"



if __name__ == '__main__':
    flask_app.run(host='0.0.0.0', port=5000, debug=True)