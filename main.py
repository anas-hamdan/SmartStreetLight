from smart_street_light import SmartStreetLight


if __name__ == '__main__':
    smart_street_light = SmartStreetLight()
    try:
        while True:
            smart_street_light.run()

    except KeyboardInterrupt:
        print("Passed objects:", smart_street_light.passed_objects)
        print("System stopped by User")

    finally:
        smart_street_light.reset()
