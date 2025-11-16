@echo off
echo Starting Modbus RTU Simulator on COM10...
python src/simulator/modbus_simulator.py --type rtu --serial-port COM10 --baudrate 9600
pause
