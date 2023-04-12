import os
import re
import requests


def print_info(msg):
    if msg[0] == "p": return
    print(*msg, sep="\t")


class Trace:
    __ip_api = "http://ip-api.com/json/"
    __counter = 0
    __ipregex = r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}"

    def __init__(self, target :str, jumps=10):
        self.__jumps = jumps
        self.__counter = 0
        self.__target = target

    def setup(self):
        print("Work in progress...")
        try:
            if self.__jumps > 0:
                obj = os.popen(f"tracert -h {self.__jumps} {self.__target}").read()
            else:
                obj = os.popen(f"tracert {self.__target}").read()
        except BaseException as e:
            print(e)
            exit(1)
        r = re.findall(self.__ipregex, obj)
        for i in r[1:]:
            msg = self.get_info(i)
            if len(msg) != 1:
                print_info(msg)
        if self.__counter == 0:
            print("invalid query")

    def get_info(self, ip):
        try:
            response = requests.get(url=self.__ip_api + ip).json()
            if response.get('status') == "success":
                self.__counter += 1
                return [self.__counter, response.get('query'),
                        response.get('country'), response.get('isp'), response.get('as').split(" ")[0]]
            else:
                return response.get('message')
        except requests.exceptions.ConnectionError as e:
            print(e)


def main():
    target = input("Input target: ")
    jumps = input("Input jumps: ")
    app = Trace(target, int(jumps))
    app.setup()


if __name__ == '__main__':
    main()