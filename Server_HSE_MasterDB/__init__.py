from flask import Flask
from flask_login import UserMixin
from flask_sqlalchemy  import SQLAlchemy
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, 
'./Server_HSE_LoginDB_All_Modules/Server_HSE_LoginDB_Database/database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from Server_HSE_MasterDB import routes
from Server_HSE_MasterDB.Server_HSE_MasterDB_All_Modules.Server_HSE_MasterDB_Models import Server_HSE_MasterDB_Model
Server_HSE_MasterDB_Model.HSE_MasterDB_BackEnd_CreateTable()

