%TEST1 Code for communicating with an instrument.
%
%   This is the machine generated representation of an instrument control
%   session. The instrument control session comprises all the steps you are
%   likely to take when communicating with your instrument. These steps are:
%   
%       1. Create an instrument object
%       2. Connect to the instrument
%       3. Configure properties
%       4. Write and read data
%       5. Disconnect from the instrument
% 
%   To run the instrument control session, type the name of the file,
%   test1, at the MATLAB command prompt.
% 
%   The file, TEST1.M must be on your MATLAB PATH. For additional information 
%   on setting your MATLAB PATH, type 'help addpath' at the MATLAB command 
%   prompt.
% 
%   Example:
%       test1;
% 
%   See also SERIAL, GPIB, TCPIP, UDP, VISA, BLUETOOTH, I2C, SPI.
% 
 
%   Creation time: 17-May-2017 14:23:19

% Find a tcpip object.
obj1 = instrfind('Type', 'tcpip', 'RemoteHost', '169.254.105.235', 'RemotePort', 9221, 'Tag', '');

% Create the tcpip object if it does not exist
% otherwise use the object that was found.
if isempty(obj1)
    obj1 = tcpip('169.254.105.235', 9221);
else
    fclose(obj1);
    obj1 = obj1(1)
end

% Connect to instrument object, obj1.
fopen(obj1);

% Communicating with instrument object, obj1.
fprintf(obj1, 'op1 1');

% Disconnect from instrument object, obj1.
fclose(obj1);

% Configure instrument object, obj1.
set(obj1, 'Name', 'TCPIP-169.254.105.235');
set(obj1, 'RemoteHost', '169.254.105.235');

% Connect to instrument object, obj1.
fopen(obj1);

% Communicating with instrument object, obj1.
fprintf(obj1, 'op1 0');     %Output is OFF
fprintf(obj1, 'i1 0.05');      %Set I=1A
fprintf(obj1, 'v1 10');     %Set U=10V
fprintf(obj1, 'op1 1');     %Output is ON
reference = 2;
I_komanda = 0.05;
ieslegts = 1;

while ieslegts
data1 = query(obj1, 'v1o?');    %Measure voltage
data2 = query(obj1, 'i1o?');    %Measure current
data1(regexp(data1,'[A,V]'))=[];
data2(regexp(data2,'[A,V]'))=[];
spriegums = str2double(data1);  %Get voltage value
strava = str2double(data2);     %Get current value
jauda = spriegums*strava        %Calculate power
kluda = reference - jauda;
kluda = kluda / 50;
ref2 = 'i1 ';
I_komanda = I_komanda + kluda;
komandax = num2str(I_komanda, '%.3f');
ref2 = [ref2 komandax];
fprintf(obj1, ref2);
pause(1);
end



% Disconnect all objects.
fclose(obj1);

% Clean up all objects.
delete(obj1);

