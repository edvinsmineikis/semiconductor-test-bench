from devices import *
from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS



ps = PowerSupply(stop_discovery=True)
ps_small = PowerSupplySmall(stop_discovery=True)
osc = Oscilloscope(stop_discovery=True)
board = ControlBoard()

app = Flask("semiconductor-test-bench")
app.config["JSON_AS_ASCII"] = False
CORS(app)
api = Api(app)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 


