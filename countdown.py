import time
from datetime import datetime, timedelta
import logging
try:
    import keyboard  # Optional ESC support
except Exception:
    keyboard = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def get_deadline():
    while True:
        try:
            deadline_str = input("Enter the deadline (DD-MM-YYYY HH:MM): ")
            deadline = datetime.strptime(deadline_str, "%d-%m-%Y %H:%M")
            if deadline < datetime.now():
                logging.warning("The deadline must be in the future. Please try again.")
            else:
                return deadline
        except ValueError:
            logging.error("Invalid format. Please enter the deadline in the format DD-MM-YYYY HH:MM.")

def display_countdown(deadline):
    if keyboard:
        print("Press 'Esc' to exit the countdown.\n")
    else:
        print("Countdown running. Esc exit is unavailable in this environment.\n")
    while True:
        now = datetime.now()
        remaining_time = deadline - now
        if remaining_time <= timedelta(0):
            print("The deadline has passed!")
            logging.info("The countdown has ended.")
            break
        #print("------------------------------------------------------------------------------------------------------")
        print(f"|-------------------Time remaining:-------------------{remaining_time}-------------------|", end='\r')
        #print("------------------------------------------------------------------------------------------------------")

        time.sleep(0.1)  # Aggiornamento più frequente
        if keyboard and keyboard.is_pressed('esc'):
            print("\nCountdown terminated by user.")
            time_terminated = deadline - now
            days = time_terminated.days
            seconds = time_terminated.seconds
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            if days > 0:
                logging.info(f"The countdown was terminated by the user {days} days earlier.\n---     Loser you could have waitied these few days more, ... No words")
            elif hours > 0:
                logging.info(f"The countdown was terminated by the user {hours} hours earlier.\n---     You suck")
            elif minutes > 0:
                logging.info(f"The countdown was terminated by the user {minutes} minutes earlier.\n---     You suck")
            else:
                logging.info(f"The countdown was terminated by the user {seconds} seconds earlier.\n---     You suck")
            break

def main():
    print("Welcome to the Countdown Timer Viewer!")
    deadline = get_deadline()
    display_countdown(deadline)

if __name__ == "__main__":
    main()