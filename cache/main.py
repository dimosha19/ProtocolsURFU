import binascii
import pickle
import socket

import binparser
remote_server = '213.180.193.1'
remote_port = 53
_cache = {}

import signal


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.kill_now = True
        dump_cache(_cache)


def dump_cache(cache):
    with open('cache', 'wb') as cache_file:
        pickle.dump(cache, cache_file)


def load_cache() -> dict:
    try:
        with open('cache', 'rb+') as cache_file:
            cache = pickle.load(cache_file)
            return cache
    except FileNotFoundError:
        return {}


def receive_from(_socket):
    _socket.settimeout(2)
    try:
        data, addres = _socket.recvfrom(512)
    except:
        data = ''
        addres = ('', 0)
        return data, addres
    return data, addres


def DNS(local_buffer, local_addr, remote_socket):
    if len(local_buffer) and len(local_addr[0]):
        try:
            remote_socket.sendto(local_buffer, (remote_server, remote_port))
        except:
            print('Can not send DNS to remote.')
        remote_buffer, remore_addr = receive_from(remote_socket)
        if len(remote_buffer):
            return remote_buffer
    return None


def server_loop(local_host, local_port):
    killer = GracefulKiller()

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((local_host, local_port))
    except:
        print(f"Failed to listen on {local_host}:{local_port}")
        exit(1)
    print(f"Listening on {local_host}:{local_port}")

    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while not killer.kill_now:

        query, addr = receive_from(server)

        if query != "":
            q = binparser.Query(binascii.hexlify(query).decode("utf-8"))
            if q.name in _cache:
                if q.type in _cache[q.name]:
                    print("getting from cache...")
                    server.sendto(binascii.unhexlify(q.transactionID + _cache[q.name][q.type].build()), addr)
                else:
                    print(f"no type {q.type} in cache for {q.name}, go to DNS...")
                    answer = DNS(query, addr, remote_socket)
                    answer = binascii.hexlify(answer).decode("utf-8")

                    r = binparser.Response(answer)

                    _cache[r.name][r.type] = r

                    server.sendto(binascii.unhexlify(answer), addr)
            else:
                print(f"no {q.name} in cache, go to DNS...")
                answer = DNS(query, addr, remote_socket)
                answer = binascii.hexlify(answer).decode("utf-8")
                r = binparser.Response(answer)

                _cache[r.name] = {}
                _cache[r.name][r.type] = r

                server.sendto(binascii.unhexlify(answer), addr)

        for i in _cache:
            for j in _cache[i]:
                if _cache[i][j].filter():
                    del _cache[i]

    print("Server was gracefully shutdown")


def main():
    global _cache
    data = load_cache()
    for i in data:
        for j in data[i]:
            if data[i][j].filter():
                del data[i]
    _cache = data
    server_loop('127.0.0.1', 53)


if __name__ == '__main__':
    main()
