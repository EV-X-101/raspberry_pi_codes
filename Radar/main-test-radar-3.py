import RPi.GPIO as GPIO
import time

# Ultrasonic Sensor 1 GPIO pins
TRIG_PIN_1 = 20
ECHO_PIN_1 = 21

# Ultrasonic Sensor 2 GPIO pins
TRIG_PIN_2 = 4
ECHO_PIN_2 = 10

# Servo Motor 1 GPIO pin
SERVO_PIN_1 = 12

# Servo Motor 2 GPIO pin
SERVO_PIN_2 = 16

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG_PIN_1, GPIO.OUT)
GPIO.setup(ECHO_PIN_1, GPIO.IN)
GPIO.setup(TRIG_PIN_2, GPIO.OUT)
GPIO.setup(ECHO_PIN_2, GPIO.IN)
GPIO.setup(SERVO_PIN_1, GPIO.OUT)
GPIO.setup(SERVO_PIN_2, GPIO.OUT)

# Create a PWM object for the servo motors
servo_pwm_1 = GPIO.PWM(SERVO_PIN_1, 50)  # 50 Hz frequency
servo_pwm_2 = GPIO.PWM(SERVO_PIN_2, 50)  # 50 Hz frequency

# Function to set the angle of the servo motor
def set_servo_angle(servo_pwm, current_angle, target_angle):
    if target_angle < 0:
        target_angle = 0
    elif target_angle > 180:
        target_angle = 180
    
    if current_angle < 0:
        current_angle = 0
    elif current_angle > 180:
        current_angle = 180

    angle_diff = abs(target_angle - current_angle)
    increment = 1 if target_angle > current_angle else -1

    for angle in range(current_angle, target_angle, increment):
        duty_cycle = angle / 18.0 + 2.5
        servo_pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(0.01)  # Adjust the delay as per your requirement
    
    # Update the current angle to the target angle
    current_angle = target_angle
    
    return current_angle

# Function to get distance from ultrasonic sensor
def get_distance(trig_pin, echo_pin):
    GPIO.output(trig_pin, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(trig_pin, GPIO.LOW)

    pulse_start = 0
    pulse_end = 0

    while GPIO.input(echo_pin) == GPIO.LOW:
        pulse_start = time.time()

    while GPIO.input(echo_pin) == GPIO.HIGH:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

try:
    # Initialize the servo motors
    servo_pwm_1.start(0)
    servo_pwm_2.start(0)
    current_angle_1 = 0
    current_angle_2 = 0

    # Perform scanning
    direction_1 = 1  # 1 for forward, -1 for backward
    direction_2 = 1
    angle_1 = 0
    angle_2 = 0

    while True:
        if angle_1 >= 180:
            direction_1 = -1  # Change direction to move backward
        elif angle_1 <= 0:
            direction_1 = 1   # Change direction to move forward

        if angle_2 >= 180:
            direction_2 = -1  # Change direction to move backward
        elif angle_2 <= 0:
            direction_2 = 1   # Change direction to move forward

        angle_1 += direction_1 * 10  # Increment or decrement the angle by 10 degrees
        angle_2 += direction_2 * 10
        current_angle_1 = set_servo_angle(servo_pwm_1, current_angle_1, angle_1)
        current_angle_2 = set_servo_angle(servo_pwm_2, current_angle_2, angle_2)
        time.sleep(0.1)  # Delay for the servos to reach the desired angle

        dist_1 = get_distance(TRIG_PIN_1, ECHO_PIN_1)
        dist_2 = get_distance(TRIG_PIN_2, ECHO_PIN_2)
        print(f"Angle 1: {current_angle_1} | Distance 1: {dist_1} cm")
        print(f"Angle 2: {current_angle_2} | Distance 2: {dist_2} cm")
        time.sleep(0.5)

except KeyboardInterrupt:
    servo_pwm_1.stop()
    servo_pwm_2.stop()
    GPIO.cleanup()
