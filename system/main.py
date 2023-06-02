from instruments import *
import stress_tests
import measurements
from flask import Flask, request
from flask_cors import CORS
import json

app = Flask('semiconductorTestBench')
app.config['JSON_AS_ASCII'] = False
CORS(app)

@app.route('/instruments', methods=['POST'])
def instruments_route():
    if request.method == 'POST':
        try:
            target = request.json['target']
            command = request.json['command']
            resp = instruments[target].query(command)
            return resp
        except Exception as err:
            return {
                'serverError': str(type(err)) + ' - ' + str(err)
            }

@app.route('/measurements', methods=['POST'])
def measurements_route():
    if request.method == 'POST':
        try:
            pass
        except Exception as err:
            return {
                'serverError': str(type(err)) + ' - ' + str(err)
            }

instruments = {
    #"Oscilloscope": Oscilloscope()
    #"PowerSupply": PowerSupply(),
    "ControlBoard": ControlBoard()
}
#instruments['Oscilloscope'].write('DATA:SOURCE CH3')
#instruments['Oscilloscope'].write('HORIZONTAL:SCALE 1e-2')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



