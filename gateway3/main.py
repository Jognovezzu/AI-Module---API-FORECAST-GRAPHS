import time

import requests
import serial

import buffer
import data_checker
import insole_package
import task_scheduler


# Gateway Settings
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE   = 115200

# AI API Settings
AI_API_ROUTE = 'https://gait.uea.edu.br:8081/ai-module'


def send(url: str, insolePackage: insole_package.InsolePackage, buffer: buffer.Buffer) -> None:
    package = insolePackage.getCurrentData()

    if package['leftInsoleId'] is not None and package['rightInsoleId'] is not None:
        buffer.enqueue(package)
    else:
        print('Insole IDs must not be None. Check if both the insoles are connected.')
        
    try:
        firstPackage = buffer.peek()
        if firstPackage is not None:
            requests.post(url, json=firstPackage)
            print('Package has been sent to API')
            print(firstPackage)
            buffer.dequeue()
        else:
            print('There is not any package to send to API')
    except requests.exceptions.ConnectionError:
        print('Failed to connect to API')

def main():
    serialCom = serial.Serial(SERIAL_PORT, BAUD_RATE)
    insolePackage = insole_package.InsolePackage()
    packageBuffer = buffer.Buffer(maxSize=3)
    requestScheduler = task_scheduler.TaskScheduler(task=send, taskArgs=(AI_API_ROUTE, 
                                                    insolePackage, packageBuffer), delay=10)
    requestScheduler.start()
    try:
        while True:
            receivedData = serialCom.readline().rstrip()
            if data_checker.isValid(receivedData):
                print(receivedData)
                receivedDataList = receivedData.split()
                receivedDataList.append(time.strftime('%Y-%m-%d %H:%M:%S'))  #include datetime to the registry
                insolePackage.add(receivedDataList)

            else:
                print(f'{receivedData} has an invalid format')

    except KeyboardInterrupt:
       serialCom.close()


if __name__ == '__main__':
    main()
