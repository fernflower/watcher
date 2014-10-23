import sys
import time


def main():
    try:
        while True:
            time.sleep(1)
            print("ok!")
    except KeyboardInterrupt:
        print("exiting")
        sys.exit(0)


if __name__ == "__main__":
    main()
