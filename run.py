import os
from dotenv import load_dotenv
from app import create_app

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
