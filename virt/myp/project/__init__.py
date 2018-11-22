#################
#### imports ####
#################
from flask import Flask
from flask_rbac import RBAC # for RBAC (Role Base Access Control )

################
#### config ####
################

app = Flask(__name__,template_folder='templates',static_folder='static')
from . import views