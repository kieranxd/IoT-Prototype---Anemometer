# IoT-Prototype Anemometer
CMIDAT01K-DATA-SCIENCE-for-IOT Assignment

## How it works
Most anemometers use three or four arms with scoups on the end of them. 

![Image1](https://www.science-sparks.com/wp-content/uploads/2023/02/anemometer-1024x681.jpeg)

The way the rotation of the scoops are tracked is by using a reed switch. The reed switch is a switch that triggers by magnetism. Normally the "gate" of the switch is opened, but when a magnet is being help closeby it closes so current can pass through. 

![Image2](https://i1.wp.com/www.reed-sensor.com/wp-content/uploads/drawing_Reedswitch_parts.png?fit=385%2C205&ssl=1)

The rotating middle part of the anemometer has a little magnet attatched to it, so every times it rotates, it will pass over the reed switch and a signal will be sent to a Raspberry PI, where the signals are converted to a specific wind speed.

## Raspberry PI Code Explanation
The code used for this prototype is written in Python and is tested on a Rapsberry PI 4 Model B

### Packages and Global Variables
At the top of the file a few packages are imported which are necessary for the code to rum;
* ```Button``` from the gpiozero package is used to read out the signals of the reed switch.
* ```time``` is used to make sure it takes a reading every 5 seconds
* ```math``` is used to use specific mathematical constants.
* ```requests``` is used to make http requests to the "thingspeak" website that displays the graph with all the readings.

The global variables that are used are specifications about the anemometer.
* ```wind_count``` will increase every time the rotor will make a full 360 degree turn.
* ```radius_cm``` is the radius of the rotor in cm
* ```wind_interval``` is the interval that will be measured over. In this case it will be a 1s interval
* ```adjustment``` this is a calibration value. More information about this in this [datasheet](https://www.argentdata.com/files/80422_datasheet.pdf)

```python
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
```

### Wind speed calculation

#### Spin function
* The ```spin()``` function triggers every time the magnet passes over the reed switch.

```python
def spin():
    global wind_count
    wind_count = wind_count + 1
```
* To make the spin function trigger this piece of code will get executed every time the reed switch gets triggered
```python
wind_speed_sensor = Button(5)
wind_speed_sensor.when_pressed = spin
```

#### Calulate Speed function

```python
def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0

    dist_km = (circumference_cm * rotations) / 100000.0

    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 * adjustment

    m_per_second = km_per_hour / 3.6
    return m_per_second
```

* The function starts by calculating the circumference of the anemometer using the radius value passed in. The variable ```wind_count``` is used to calculate the number of full rotations made by the anemometer.

```python
def calculate_speed(time_sec):
    global wind_count
    circumference_cm = (2 * math.pi) * radius_cm
    rotations = wind_count / 2.0
```
* Using the circumference and the number of rotations, the distance traveled by the anemometers rotor is calculated in kilometers.
```python
    dist_km = (circumference_cm * rotations) / 100000.0
```
* The speed of the anemometers rotor is then calculated in kilometers per second and kilometers per hour. The adjustment factor is applied here to calibrate the speed measurement.
```python
    km_per_sec = dist_km / time_sec
    km_per_hour = km_per_sec * 3600 * adjustment
```
* Finally, the speed is converted from kilometers per hour to meters per second and returned as the output of the function.
```python
    m_per_second = km_per_hour / 3.6
    return m_per_second
```

### Sending requests

Requests to the ThingSpeak channel are handled by these two functions
```python
def sendDataKN(speed):
    wind_speed_kn = speed / 1.852
    queries = {"api_key": writeAPIkey,
               "field1": wind_speed_kn}

    r = requests.get(url, params=queries)
    if r.status_code == requests.codes.ok:
        print("Data Received! " + str(r.status_code))
    else:
        print("Error Code: " + str(r.status_code))
```
```python
def sendDataMS(speed):
    wind_speed_ms = speed
    queries = {"api_key": writeAPIkey,
               "field2": wind_speed_ms}

    r = requests.get(url, params=queries)
    if r.status_code == requests.codes.ok:
        print("Data Received! " + str(r.status_code))
    else:
        print("Error Code: " + str(r.status_code))
```
* The only difference between the two functions is that the sendDataKN function starts by converting the input wind speed from meters per second to knots. This is done by dividing the input speed value by 1.852, which is the conversion factor from meters per second to knots.
```python
    wind_speed_kn = speed / 1.852
```

* Next, the function sets up the query parameters for the ThingSpeak API call. It creates an object called queries with two key-value pairs: api_key, which is the write API key for the ThingSpeak channel, and field1, which is the field in the channel to which the wind speed value will be written. The wind speed in knots is stored as the value for field1.
```python
    queries = {"api_key": writeAPIkey,
               "field1": wind_speed_kn}
```

* The function then sends an HTTP GET request to the ThingSpeak API URL with the queries object as the query parameters. The requests.get() function is used from the requests module to send the GET request.
```python
    r = requests.get(url, params=queries)
```

* Finally, the function checks the HTTP response code from the ThingSpeak API. If the response code is 200, which corresponds to a successful request, the function prints a success message to the console. Otherwise, an error message is printed.
```python
    if r.status_code == requests.codes.ok:
        print("Data Received! " + str(r.status_code))
    else:
        print("Error Code: " + str(r.status_code))
```

### Looping the functions
* This piece of code makes sure that every 5 seconds, new data is sent to the ThingSpeak channel.
```python
while True:
    wind_count = 0
    time.sleep(5)
    speed = calculate_speed(wind_interval)
    print("Wind Speed: %0.1f m/s (%0.1f knots)" % (speed, speed * 1.944))
    sendDataKN(speed)
    sendDataMS(speed)
```

## ThingSpeak Chart
Sometimes it takes a while for the charts to update, that's why there are some steep ups and downs.

![image3](https://i.gyazo.com/43114477ccc72212dc9b10ac0b731838.png)

## Pipeline
![image4](https://i.imgur.com/mqNor05.png)
