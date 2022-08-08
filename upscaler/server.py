import time
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    logging.info('Start')
    while True:
        time.sleep(1)    


if __name__ == "__main__":
        main()
