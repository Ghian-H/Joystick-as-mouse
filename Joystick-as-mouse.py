import serial
import pyautogui
import time

# --- CONFIGURATION ---
PORT = 'COM3'         # Change to your Arduino COM port
BAUD = 9600
DEADZONE = 100        # Higher deadzone prevents drift from loose springs
SPEED_DIVISOR = 20    # Lower = faster cursor, Higher = slower cursor

pyautogui.FAILSAFE = False

try:
    # Short timeout prevents script lag
    ser = serial.Serial(PORT, BAUD, timeout=0.02)
    time.sleep(2)
    print("Connected to Arduino!")
    print("--> CALIBRATING: LET GO OF JOYSTICK FOR 2 SECONDS... <--")
except Exception as e:
    print(f"Connection error on {PORT}: {e}")
    print("Ensure the Arduino IDE Serial Monitor is CLOSED.")
    exit()

# Calibrate resting position
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
        # FIX: If serial data builds up in memory, clear it so movements are instant
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

            # Calculate movement relative to calibrated center
            dx_raw = x_val - CENTER_X
            dy_raw = y_val - CENTER_Y

            # X Axis Movement
            dx = 0
            if abs(dx_raw) > DEADZONE:
                dx = dx_raw // SPEED_DIVISOR

            # Y Axis Movement (Inverted: Pushing UP moves cursor UP)
            dy = 0
            if abs(dy_raw) > DEADZONE:
                dy = -(dy_raw // SPEED_DIVISOR)

            # Move mouse
            if dx != 0 or dy != 0:
                pyautogui.moveRel(dx, dy)

            # Left Click
            if sw_val == 0 and last_sw == 1:
                pyautogui.click(button='left')

            last_sw = sw_val

    except KeyboardInterrupt:
        print("\nJoystick control stopped.")
        break
    except Exception:
        pass 