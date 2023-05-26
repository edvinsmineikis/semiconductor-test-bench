from instruments import *
import stress_tests
import measurements
from flask import Flask, request
from flask_cors import CORS
import json


app = Flask('semiconductorTestBench')
app.config['JSON_AS_ASCII'] = False
CORS(app)


instruments = {
    "Oscilloscope": Oscilloscope()
    #"PowerSupply": PowerSupply(),
    #"ControlBoard": ControlBoard()
}
instruments['Oscilloscope'].set_channel(3)
instruments['Oscilloscope'].set_horizontal_scale('1e-2')

@app.route('/commands', methods=['GET', 'POST'])
def commands():
    if request.method == 'GET':
        msg = {
            'content': 'no content' 
        }
        return msg
    if request.method == 'POST':
        
        msg = {
            #'answer': measurements.get_curve(instruments).tolist()
            'got': measurements.get_curve(instruments).tolist()
        }
        return msg



if __name__ == '__main__':
    #stress_tests.test_twice()
    #stress_tests.test_twice()
    app.run(host='0.0.0.0', port=5000)



