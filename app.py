from icv7 import create_app, clients
from icv7.monday import BaseItem, CustomLogger

# App Creation
app = create_app()


# Routes
@app.route('/', methods=['GET'])
def index():
    print('Hello World')
    return 'Hello Returns'


if __name__ == '__main__':
    app.run()
else:
    pass
