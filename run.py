import os
from app import create_app

app = create_app()
app.static_folder = os.path.abspath("static")

if __name__ == "__main__":
    app.run(debug=True)
