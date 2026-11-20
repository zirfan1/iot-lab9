# Muhammad Zaid Irfan C22499352
# Lut Dunne C23470466
# Amar Jagana c22423526
# Ephraim Kuedituka C23504716
# Mohammad Mujahed C23502209


import time
import network
import ntptime
from machine import ADC, Pin, unique_id
from ubinascii import hexlify
from umqtt.robust import MQTTClient
from my_schema_upb2 import TemperaturemessageMessage

SSID = "Lut"
PASSWORD = "12481632"
BROKER_IP = "172.20.10.2"  
MQTT_PORT = 8080
TOPIC = b"temp/pico"

ROLE = "subscriber"  # On Pico 2, change to "subscriber"
PUBLISH_INTERVAL = 0.5

DEVICE_ID = "pico-" + hexlify(unique_id()).decode()
CLIENT_ID = DEVICE_ID.encode()
led = Pin("LED", Pin.OUT)
latest_temps = {}
MAX_AGE = 10 * 60


def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    if not wifi.isconnected():
        print("Connecting to Wi-Fi...")
        wifi.connect(SSID, PASSWORD)
        start = time.ticks_ms()
        while not wifi.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) >= 30000:
                raise OSError("Wi-Fi connection timed out")
            time.sleep_ms(250)
    print("Connected to Wi-Fi, IP:", wifi.ifconfig()[0])
    return wifi


def synchronise_time():
    try:
        ntptime.settime()
        print("Clock synchronised by NTP (UTC)")
    except Exception as err:
        print("WARNING: NTP sync failed, timestamps might be incorrect:", err)


def connect_mqtt():
    mqtt = MQTTClient(client_id=CLIENT_ID, server=BROKER_IP,
                      port=MQTT_PORT, keepalive=60)
    if ROLE == "subscriber":
        mqtt.set_callback(callback)
    mqtt.connect()
    print("Connected to MQTT broker at", BROKER_IP)
    if ROLE == "subscriber":
        mqtt.subscribe(TOPIC)
        print("Subscribed to", TOPIC)
    return mqtt


def read_temperature(sensor):
    voltage = sensor.read_u16() * (3.3 / 65535)
    return 27 - (voltage - 0.706) / 0.001721


def publish_temperature(mqtt, sensor):
    temp = read_temperature(sensor)
    msg = TemperaturemessageMessage()
    msg.publisher_id = DEVICE_ID
    msg.temperature = temp
    msg.epoch = int(time.time())
    payload = msg.serialize()  
    mqtt.publish(TOPIC, payload)
    print("Sent: {:.2f} C, publisher {}, epoch {}".format(temp, DEVICE_ID, msg.epoch._value))


def callback(topic, payload):
    if topic != TOPIC:
        return
    try:
        pb = TemperaturemessageMessage()
        if not pb.parse(payload):
            print("Message failed validation")
            return
        temp = pb.temperature._value
        pubid = pb.publisher_id._value
        epoch = pb.epoch._value
        latest_temps[pubid] = (temp, epoch)
        now = int(time.time())
        for key in list(latest_temps.keys()):
            if now - latest_temps[key][1] > MAX_AGE:
                del latest_temps[key]
        stamp = time.localtime(epoch)
        print("Received: {:.2f} C from {} at {:02d}:{:02d}:{:02d} UTC".format(
              temp, pubid, stamp[3], stamp[4], stamp[5]))
        # LED output is optional for Lab 9, but kept from Lab 8.
        led.value(1 if temp >= 25 else 0)
    except Exception as err:
        print("Error decoding Protobuf:", err)


def main():
    if ROLE not in ("publisher", "subscriber"):
        raise ValueError('ROLE must be "publisher" or "subscriber"')
    connect_wifi()
    if ROLE == "publisher":
        synchronise_time()
    mqtt = connect_mqtt()
    if ROLE == "publisher":
        sensor = ADC(4)
        while True:
            publish_temperature(mqtt, sensor)
            time.sleep(PUBLISH_INTERVAL)
    else:
        while True:
            mqtt.wait_msg()


if __name__ == "__main__":
    main()

