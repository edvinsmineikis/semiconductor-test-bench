myScope = oscilloscope()
availableResources = resources(myScope)
myScope.Resource = availableResources{1,1}
% Connect to the instrument.
connect(myScope);

%% % Automatically configuring the instrument based on the input signal.
autoSetup(myScope);

%myScope.AcquisitionTime = 0.01;

myScope.WaveformLength = 1000;

%myScope.TriggerMode = 'normal';

%myScope.TriggerLevel = 0.1;

enableChannel(myScope, 'CH1');

setVerticalCoupling (myScope, 'CH1', 'DC');

setVerticalRange (myScope, 'CH1', 5);

%% Reading waveform

%waveformArray = getWaveform(myScope);
waveformArray = getWaveform(myScope, 'acquisition', true);
timeStep = size(waveformArray);
sizeWaveform = timeStep(2)
timeStep = myScope.AcquisitionTime/timeStep(2);
timeAxis = [0:sizeWaveform-1]*timeStep*100;


% Plot the waveform.
plot(timeAxis,waveformArray);
xlabel('Milliseconds');
ylabel('Voltage');0
