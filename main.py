from gpiozero import Button
import time
import math
import requests

writeAPIkey = ""
channelID = ""
url = "https://api.thingspeak.com/update"

wind_count = 0
radius_cm = 9.0
wind_interval = 1
adjustment = 1.18


def spin():
    global wind_count
    wind_count = wind_count + 1


def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0

    dist_km = (circumference_cm * rotations) / 100000.0

    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 * adjustment

    m_per_second = km_per_hour / 3.6
    return m_per_second


wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin


def sendDataKN(speed):
    wind_speed_kn = speed / 1.852
    queries = {"api_key": writeAPIkey,
               "field1": wind_speed_kn}

    r = requests.get(url, params=queries)
    if r.status_code == requests.codes.ok:
        print("Data Received! " + str(r.status_code))
    else:
        print("Error Code: " + str(r.status_code))


def sendDataMS(speed):
    wind_speed_ms = speed
    queries = {"api_key": writeAPIkey,
               "field2": wind_speed_ms}

    r = requests.get(url, params=queries)
    if r.status_code == requests.codes.ok:
        print("Data Received! " + str(r.status_code))
    else:
        print("Error Code: " + str(r.status_code))


while True:
    wind_count = 0
    time.sleep(5)
    speed = calculate_speed(wind_interval)
    print("Wind Speed: %0.1f m/s (%0.1f knots)" % (speed, speed * 1.944))
    sendDataKN(speed)
    sendDataMS(speed)
