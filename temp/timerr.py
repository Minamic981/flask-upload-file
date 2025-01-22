import time
import keyboard  # To detect keypresses

def stopwatch():
    print("Stopwatch started. Press 'K' to stop.")

    start_time = time.time()  # Record the start time
    while True:
        elapsed_time = time.time() - start_time  # Calculate elapsed time
        print(f"\rElapsed Time: {elapsed_time:.2f} seconds", end="")  # Print time dynamically
        time.sleep(0.1)  # Update every 0.1 seconds

        if keyboard.is_pressed('k'):  # Stop if 'K' is pressed
            print("\nStopwatch stopped.")
            break

if __name__ == "__main__":
    stopwatch()
