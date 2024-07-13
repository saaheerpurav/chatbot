from waitress import serve
from app import create_app

app = create_app()

if __name__ == "__main__":
    if app.config["ENV"] == "dev":
        app.run(debug=True)

    elif app.config["ENV"] == "prod":
        serve(app, host="0.0.0.0", port=8080)
