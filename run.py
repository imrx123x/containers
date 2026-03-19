from app import create_app
from app.db import init_db, wait_for_db

app = create_app()

if __name__ == "__main__":
    wait_for_db()
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)