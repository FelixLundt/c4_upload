from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)  # Debug mode gives us auto-reload and better error messages 