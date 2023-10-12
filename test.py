import sys

def print_hello(number):
    print("hello", number)

if __name__ == "__main__":
    print(sys.argv)
    print_hello(sys.argv[1])