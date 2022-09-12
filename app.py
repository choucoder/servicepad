from decouple import config
from flasgger import Swagger
from flask import Flask
from flask_migrate import Migrate

from core.api import CustomApi
from database.connection import db
from v1.routes import routes
 

app = Flask(__name__)

SWAGGER_TEMPLATE = {
    "securityDefinitions": {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": "x-access-token",
            "in": "header"
        }
    }
}

swagger = Swagger(app, template=SWAGGER_TEMPLATE)
api = CustomApi(app)

api.add_resources(routes)
app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{config('DB_USERNAME')}:{config('DB_PASSWORD')}@localhost:5432/{config('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db.init_app(app)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=config('DEBUG'), port=config('PORT'))
