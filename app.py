from icv7 import create_app, clients
from icv7.monday import BaseItem, CustomLogger

# App Creation
app = create_app()


# Routes
# Index/Home
@app.route('/', methods=['GET'])
def index():
    print('Hello World')
    return 'Hello Returns'


@app.route('/monday/repairers/get-pc-report', methods=['POST'])
def repairers_pc_report_fetch():
    pass


if __name__ == '__main__':
    app.run()
