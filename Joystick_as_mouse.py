import serial
import pyautogui
import time

PORT = 'COM3'        
DEADZONE = 100        
SPEED_DIVISOR = 20   

INVERT_X = False      
INVERT_Y = True      

pyautogui.FAILSAFE = False

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.02)
    time.sleep(2)
    print("Connected to Arduino!")
    print("--> CALIBRATING: LET GO OF JOYSTICK FOR 2 SECONDS... <--")
except Exception as e:
    print(f"Connection error on {PORT}: {e}")
    print("Ensure the Arduino IDE Serial Monitor is CLOSED.")
    exit()

x_samples, y_samples = [], []
start_time = time.time()

while time.time() - start_time < 2:
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        parts = line.split(',')
        if len(parts) >= 2:
            try:
                x_samples.append(int(parts[0]))
                y_samples.append(int(parts[1]))
            except ValueError:
                pass

CENTER_X = sum(x_samples) // len(x_samples) if x_samples else 509
CENTER_Y = sum(y_samples) // len(y_samples) if y_samples else 501
print(f"Calibration Complete! Center: X={CENTER_X}, Y={CENTER_Y}")
print("Joystick ACTIVE. Press Ctrl+C in terminal to stop.")

last_sw = 1

while True:
    try:
       
        if ser.in_waiting > 50:
            ser.reset_input_buffer()

        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line:
            continue

        parts = line.split(',')
        if len(parts) >= 2:
            x_val = int(parts[0])
            y_val = int(parts[1])
            sw_val = int(parts[2]) if len(parts) >= 3 else 1

            dx_raw = x_val - CENTER_X
            dy_raw = y_val - CENTER_Y

     
            dx = (dx_raw // SPEED_DIVISOR) if abs(dx_raw) > DEADZONE else 0
            dy = (dy_raw // SPEED_DIVISOR) if abs(dy_raw) > DEADZONE else 0

       
            if INVERT_X:
                dx = -dx
            if INVERT_Y:
                dy = -dy

      
            if dx != 0 or dy != 0:
                pyautogui.moveRel(dx, dy)

            if sw_val == 0 and last_sw == 1:
                pyautogui.click(button='left')

            last_sw = sw_val

    except KeyboardInterrupt:
        print("\nJoystick control stopped.")
        break
    except Exception:
        pass
