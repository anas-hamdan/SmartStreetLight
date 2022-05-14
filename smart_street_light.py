import RPi.GPIO as GPIO
import requests

import time

from constants import SystemMode, SystemGPIO, DISTANCE_THRESHOLD, GET_KEY, POST_KEY


class SmartStreetLight(object):

    def __init__(self, system_mode=SystemMode.SMART, gpio_trigger=SystemGPIO.TRIGGER, gpio_echo=SystemGPIO.ECHO, gpio_led=SystemGPIO.LED):
        """
        initialize system
        :param (str) system_mode: ON, OFF, SMART. how system will work
        :param gpio_trigger: trigger GPIO number for ultrasonic sensor
        :param gpio_echo: echo GPIO number for ultrasonic sensor
        :param gpio_led: led GPIO number
        """
        # GPIO Mode (BOARD / BCM)
        GPIO.setmode(GPIO.BCM)

        # set GPIO Pins
        self.gpio_trigger = gpio_trigger
        self.gpio_echo = gpio_echo
        self.gpio_led = gpio_led

        # set GPIO direction (IN / OUT)
        GPIO.setup(self.gpio_trigger, GPIO.OUT)
        GPIO.setup(self.gpio_echo, GPIO.IN)
        GPIO.setup(self.gpio_led, GPIO.OUT)

        # set system's mode
        self.system_mode = system_mode

        # set maximum distance required to turn lights on
        self.distance_threshold = DISTANCE_THRESHOLD

        # set the count of passed objects to Zero
        self.passed_objects = 0

        # set sleep time in seconds
        self.sleep_time = 10

    def run(self):
        if self.system_mode == SystemMode.SMART:
            self.turn_lights_smart()

        elif self.system_mode == SystemMode.ON:
            self.turn_lights_on()

        elif self.system_mode == SystemMode.OFF:
            self.turn_lights_off()

        else:
            raise Exception("Wrong system mode.")
        
        time.sleep(0.5)
        
    def send_data(self):
                     
        url = "https://api.thingspeak.com/update.json" 
        params = {
            "api_key": POST_KEY,
            "field1": self.system_mode, 
            "field2": self.get_status(), 
            "field3": self.passed_objects
        }    
        response = requests.get(url, params=params)
        print(response.json()) 

    def reset(self):
        GPIO.cleanup()
        self.passed_objects = 0

    def turn_lights_on(self, duration=None):
        """
        turns lights on if they are off
        :param (int) duration: sleep time in seconds until the next action
        :return:
        """
        
        if not GPIO.input(self.gpio_led):
            GPIO.output(self.gpio_led, True)
            print("Turning lights on for %.1f seconds" % duration)
        
        self.send_data()
        
        if duration:
            time.sleep(duration)

    def turn_lights_off(self, duration=None):
        """
        turns light off if they are on
        :param (int) duration: sleep time in seconds until the next action
        :return:
        """
        if GPIO.input(self.gpio_led):
            GPIO.output(self.gpio_led, False)

        if duration:
            time.sleep(duration)

    def turn_lights_smart(self, log=True):
        """
        turns light on or off based on smart logic
        :param (boolean) log: if True prints measured distance
        :return:
        """
        distance = self._get_distance()

        if log:
            print("Distance = %.1f cm" % distance)

        if distance <= self.distance_threshold:
            print("Object detected at %.1f cm" % distance)
            self.passed_objects = self.passed_objects + 1
            self.turn_lights_on(duration=self.sleep_time)

        else:
            self.turn_lights_off()

    def _get_distance(self):
        """
        calculates the distance between sensor and object
        :return (float): distance
        """
        # set Trigger to HIGH
        GPIO.output(self.gpio_trigger, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.gpio_trigger, False)

        start_time = time.time()
        stop_time = time.time()

        # save StartTime
        while GPIO.input(self.gpio_echo) == 0:
            start_time = time.time()

        # save time of arrival
        while GPIO.input(self.gpio_echo) == 1:
            stop_time = time.time()

        # time difference between start and arrival
        time_elapsed = stop_time - start_time

        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (time_elapsed * 34300) / 2

        return distance

    def set_mode(self, mode):
        if not mode:
            return

        if not (mode == SystemMode.SMART or mode == SystemMode.OFF or mode == SystemMode.ON):
            print("not valid system mode")
        else:
            self.system_mode = mode
            print("System mode is:", mode)
    
    def get_status(self):
        return "lights on" if GPIO.input(self.gpio_led) else "lights off"



