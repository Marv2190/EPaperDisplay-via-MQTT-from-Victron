#!/usr/bin/env python3

import paho.mqtt.client as mqtt
import json
import sys
import os
import logging
import time
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13d

cerboserial = "cerboserial"# Ist auch gleich VRM Portal ID
acpower = 1
dcpower = 1
L1=1
L2=2
L3=3
pvgesamt=0
Fehler=""
akkuladen=1
se=1
ve=1
akku=1
grid=1
hausverbrauch =1
akkuladen=1
akkuspg=1
zaehler=0
neuaufbau=2000

logging.basicConfig(level=logging.DEBUG)
font17 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 17)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font15 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 15)
font10 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 10)
font16 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 16)
font12 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 12)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L1/Power")
    client.subscribe("N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L2/Power")
    client.subscribe("N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L3/Power")
    client.subscribe("N/" + cerboserial + "/system/0/Dc/Pv/Power")
    client.subscribe("N/" + cerboserial + "/pvinverter/20/Ac/Energy/Forward")
    client.subscribe("N/" + cerboserial + "/solarcharger/278/Yield/User")
    client.subscribe("N/" + cerboserial + "/vebus/276/Soc")
    client.subscribe("N/" + cerboserial + "/vebus/276/Dc/0/Voltage")
    client.subscribe("N/" + cerboserial + "/vebus/276/Ac/ActiveIn/P")
    client.subscribe("N/" + cerboserial + "/pvinverter/20/Ac/Power")
    client.subscribe("N/" + cerboserial + "/system/0/Dc/Battery/Power")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):

    try:

        global acpower,dcpower,pvgesamt,se,ve,akku, grid, hausverbrauch, akkuladen, akkuspg, zaehler, L1, L2, L3, Fehler
        # print(msg.topic+" "+str(msg.payload))
        if msg.topic == "N/" + cerboserial + "/pvinverter/20/Ac/Power":# AC PV Generation

            acpower = json.loads(msg.payload)
            acpower = int(acpower['value'])

        if msg.topic == "N/" + cerboserial + "/system/0/Dc/Pv/Power":# DC PV Generation

            dcpower = json.loads(msg.payload)
            dcpower=int(dcpower['value'])

        if msg.topic == "N/" + cerboserial + "/pvinverter/20/Ac/Energy/Forward":# Solaredge YieldALL

            se = json.loads(msg.payload)
            se = int(se['value'])

        if msg.topic == "N/" + cerboserial + "/solarcharger/278/Yield/User":# Victron YieldALL

            ve = json.loads(msg.payload)
            ve=int(ve['value'])
            print(ve)

        if msg.topic == "N/" + cerboserial + "/vebus/276/Soc":# Akkuprozent

            akku = json.loads(msg.payload)
            akku=float(akku['value'])

        if msg.topic == "N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L1/Power":# L1

            L1 = json.loads(msg.payload)
            L1=int(L1['value'])

        if msg.topic == "N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L2/Power":# L2

            L2 = json.loads(msg.payload)
            L2=int(L2['value'])

        if msg.topic == "N/" + cerboserial + "/system/0/Ac/ConsumptionOnOutput/L3/Power":# L3

            L3 = json.loads(msg.payload)
            L3=int(L3['value'])

        if msg.topic == "N/" + cerboserial + "/vebus/276/Ac/ActiveIn/P":#grid

            grid = json.loads(msg.payload)
            grid = int(grid['value'])
            grid = grid /1000

        if msg.topic == "N/" + cerboserial + "/system/0/Dc/Battery/Power":# Akkuladen

            akkuladen = json.loads(msg.payload)
            akkuladen=int(akkuladen['value'])
            akkuladen = akkuladen /1000


        if msg.topic == "N/" + cerboserial + "/vebus/276/Dc/0/Voltage":# Akkuspannung

            akkuspg = json.loads(msg.payload)
            akkuspg=float(akkuspg['value'])

        # print(acpower)
        # print(dcpower)
        zaehler=zaehler+1
        pvgesamt= acpower + dcpower
        hausverbrauch = (L1+L2+L3)/1000
        print(str(pvgesamt)+ "W PVgesamt")
        print(str(akkuladen)+ "W Akkuleistung")
        print(str(se)+ "kWh Solaredge Ertrag")
        print(str(ve)+ "kWh Victron Ertrag")
        print(str(akku)+ "% Akku")
        print(str(grid)+ "W Grid")
        print(str(hausverbrauch)+ "W hausverbrauch")
        print(str(akkuspg)+ "V Akkuspannung")
        print(str(zaehler)+"x Funktion aufgerufen")
        print("-----------------------------------")
    except:
        print("Irgendwas ist hier ziemlich schief gelaufen")


client = mqtt.Client("E-PaperDisplay")
client.on_connect = on_connect
client.on_message = on_message

client.connect("192.168.1.167", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_start()
try:
    epd = epd2in13d.EPD()
    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)

    while (True):
        if(neuaufbau == 2000):# Wenn 2000 dann wird komplettes Bild neu aufgebaut
            epd.Clear(0xFF)
            time_image = Image.new('1', (epd.height, epd.width), 0)
            time_image = Image.open(os.path.join(picdir, 'bildinv.bmp'))
            time_draw = ImageDraw.Draw(time_image)
            epd.display(epd.getbuffer(time_image))
            neuaufbau = 0
        time_draw.rectangle((130, 0, 220, 60), fill = 0) # Mal alles wieder weiß wo aktualisiert wird,Rechts
        time_draw.rectangle((35, 0, 95, 60), fill = 0) # Mal alles wieder weiß wo aktualisiert wird, Links
        time_draw.rectangle((29, 80, 83, 104), fill = 0) # Mal alles wieder weiß wo aktualisiert wird, Grid
        time_draw.rectangle((89, 80, 115, 97), fill = 0) # Mal alles wieder weiß wo aktualisiert wird, Haus
        time_draw.rectangle((121, 80, 173, 104), fill = 0) # Mal alles wieder weiß wo aktualisiert wird, Akku
        time_draw.rectangle((176, 81, 203, 97), fill = 0) # Mal alles wieder weiß wo aktualisiert wird, Akkuspg
        time_draw.text((140, 5), time.strftime('%H:%M:%S'), font = font15, fill = 255) # Uhrzeit
        time_draw.text((33, 9), str(pvgesamt)+"W", font = font17, fill = 255) # pvgesamt
        time_draw.text((127, 20), str(se)+"kWh", font = font17, fill = 255) #se
        time_draw.text((127, 36), str(ve)+"kWh", font = font17, fill = 255) #ve
        time_draw.text((35, 40), str(("%.4f" % akku)[:4])+"%", font = font17, fill = 255) #akkuprozent
        time_draw.text((89, 82), str(("%.4f" % hausverbrauch)[:4]).rstrip('0').rstrip('.'), font = font15, fill = 255) #hausverbrauch
        time_draw.text((35, 82), str(("%.4f" % grid)[:6]).rstrip('0').rstrip('.'), font = font17, fill = 255) #Grid
        time_draw.text((125, 82), str(("%.4f" % akkuladen)[:6]).rstrip('0').rstrip('.'), font = font17, fill = 255) #akkuladen
        time_draw.text((176, 84), str(("%.4f" % akkuspg)[:4])+"V", font = font12, fill = 255) #akkuspg
        # newimage = time_image.crop([10, 10, 120, 50])
        # time_image.paste(newimage, (50,30))
        epd.DisplayPartial(epd.getbuffer(time_image))
        neuaufbau = neuaufbau + 1
        neuaufbauanzeige = 2000-neuaufbau
        print("Neuaufbau  " + str(neuaufbauanzeige))
        time.sleep(30)


    client.loop_stop()

# deal with ^C
except KeyboardInterrupt:
    print("\ninterrupted!")
    client.loop_stop()