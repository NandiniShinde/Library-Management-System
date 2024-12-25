from flask import Flask

def configure_routes(app: Flask):
    @app.route('/', methods=['GET'])
    def home():
        return "Welcome to the Library Management System!"
