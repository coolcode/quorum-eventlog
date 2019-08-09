from config import application, __init_resource

app = application
__init_resource()

if __name__ == '__main__':
    # for testing
    # application.run(host=application.config['HOST'], port=application.config['PORT'], debug=application.config['DEBUG'])
    # for deployment
    app.run()
