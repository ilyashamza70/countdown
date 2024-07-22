import time
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_deadline():
    while True:
        try:
            deadline_str = input("Enter the deadline (YYYY-MM-DD HH:MM:SS): ")
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
            if deadline < datetime.now():
                logging.warning("The deadline must be in the future. Please try again.")
            else:
                return deadline
        except ValueError:
            logging.error("Invalid format. Please enter the deadline in the format YYYY-MM-DD HH:MM:SS.")

def display_countdown(deadline):
    while True:
        now = datetime.now()
        remaining_time = deadline - now
        if remaining_time <= timedelta(0):
            print("The deadline has passed!")
            logging.info("The countdown has ended.")
            break
        print(f"Time remaining: {remaining_time}", end='\r')
        time.sleep(1)

def main():
    print("Welcome to the Countdown Timer Viewer!")
    deadline = get_deadline()
    display_countdown(deadline)

if __name__ == "__main__":
    main()