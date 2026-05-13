from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder='frontend', static_url_path='/frontend')

# blueprint configure----------------
from controller.analyze_controller import analyze_bp
from controller.auth_controller import auth_bp
from controller.user_controller import user_bp
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(analyze_bp)
# ------------------------------------------

# DATABASE configure----------------------------------
from db import db
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)
migrate = Migrate(app, db)
from Models.users import Users
from Models.predictions import Predictions
# --------------------------------------------

# JWT MANAGER------------------------
from flask_jwt_extended import JWTManager
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

@app.route("/", methods=['GET'])
def default():
    return send_from_directory('frontend', 'index.html')

if __name__ == "__main__":
    app.run(debug=True)