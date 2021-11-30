from flask_cors import CORS
from flasgger import Swagger
from const import MODE_DEBUG, PORT
from app import app, socketio
from modules.authentication.authentication import auth
from modules.item.item_controller import ite
from modules.recycle.recycle_controller import recycle


CORS(app)

# registra los demas modulos
app.register_blueprint(auth)
app.register_blueprint(ite)
app.register_blueprint(recycle)


# configuracion del swagger
swagger = Swagger(app,
                  template={
                      "swagger": "2.0",
                      "basePath": "/",
                      "info": {
                          "title": "<<API_NAME>> API",
                          "version": "1.0"
                      },
                      "consumes": [
                          "application/json"
                      ],
                      "produces": [
                          "application/json"
                      ],
                      "contact": {
                          "name": "API Support",
                          "url": "http://www.example.com/support",
                          "email": "suppport@dealergeek.com"
                      }
                  })

if __name__ == '__main__':
    app.config['JSON_SORT_KEYS'] = False
    socketio.run(app, port=PORT, host='0.0.0.0', debug=MODE_DEBUG)
