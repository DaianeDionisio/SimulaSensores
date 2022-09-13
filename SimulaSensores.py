import threading
import time
import json
import re

from random import uniform
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017')
db = client['bancoiot']
sensores = db.sensores

#aqui estamos criando um lock de thread para travar o objeto enquanto a temperatura está sendo mostrada no terminal
print_lock = threading.Lock()
original_print = __builtins__.print
def print(*args, **kw):
   with print_lock:
      original_print(*args, **kw)


def consultaTemp(nomeSensor: str):
    # verificar o valor da temperatura no SensorX
    var = sensores.find({"nomeSensor": nomeSensor}, {'_id': 0, 'valorSensor': 1})

    # aqui estamos tratando o dicionario em uma string
    for c in var:
        result = c
    result1 = json.dumps(result)

    #aqui estamos tratando a string e pegando apenas o valor numerico, que é a temperatura
    result2 = ([float(s) for s in re.findall(r'-?\d+\.?\d*', result1)])
    #como o valor foi convertido para uma lista, estamos retornando o primeiro (e unico) valor da lista
    return(result2[0])

def updateTemp(nomeSensor:str, temperatura:float):
    sensores.update_one({"nomeSensor":nomeSensor},{"$set":{"valorSensor":temperatura}})

def updateAlarm(nomeSensor:str, alarme:bool):
    sensores.update_one({"nomeSensor":nomeSensor},{"$set":{"sensorAlarmado":alarme}})

temp = 0
tempdb = 0

def simulaSensor(sensor, intervalo):

    tempdb = consultaTemp(sensor)
    while tempdb<38:
        temp = uniform(30,40)
        print(sensor,': ', temp,' \n')
        time.sleep(intervalo)
        updateTemp(sensor,temp)

        if(temp>38):
            updateAlarm(sensor,True)
            print("Atenção! Temperatura muito alta! Verificar Sensor", sensor, "!")
        tempdb = consultaTemp(sensor)

    #para caso do sensor já estiver com o alarme de temperatura antes
    else:
        print("Atenção! Temperatura muito alta! Verificar Sensor", sensor, "!")

sensor1 = threading.Thread(target=simulaSensor, args=('Temp1',2))
sensor2 = threading.Thread(target=simulaSensor, args=('Temp2',2))
sensor3 = threading.Thread(target=simulaSensor, args=('Temp3',2))

sensor1.start()
sensor2.start()
sensor3.start()