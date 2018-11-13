# run.py

# Add your settings here... this is a temporary location, as the settings for a Flask app
# should be stored separate from your main program.
DEBUG = True

from project import app

if __name__ == "__main__":
    import os

    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT,debug='true')

    #hcuidhcuidhcuisdh