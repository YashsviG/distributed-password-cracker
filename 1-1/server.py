import argparse
import socket


def getHostIP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    try:
        sock.connect(('10.254.254.254', 80))
        HOST = sock.getsockname()[0]
    except Exception:
        HOST = '127.0.0.1'
    finally:
        sock.close()
    return HOST

def handle_client(conn, users_list, n_clients):
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='shadowFile', required=True)
    parser.add_argument('-t', type=int, dest='noOfClients', default=1)
    parser.add_argument('-p', type=int, dest='PORT', default=8000)
    parser.add_argument('users', nargs='+')
    args = parser.parse_args()

    HOST = getHostIP()
    PORT = args.PORT
    SHADOW_FILE = args.shadowFile
    NUMBER_OF_CLIENTS = args.noOfClients

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(NUMBER_OF_CLIENTS)

    print(f'[SERVER] Server started on {HOST}:{PORT}')

    users_list = []
    interrupted = False
    try:
        passFile = open(args.shadowFile, 'r')
        for line in passFile.readlines():
            user = line.split(":")[0]
            line2 = line.replace("\n", "").split(":")
            if user in args.users:
                if not line2[1] in ['x', '*', '!']:
                    users_list.append(line)
                else:
                    print("Cannot crack passwords starting with !, x, *")

        if len(users_list) < len(args.users):
            print(f'{len(args.users) - len(users_list)} user(s) not found')

        while True:
            conn, addr = server_socket.accept()
            handle_client(conn, users_list)

        # for user in users_list:
        #     crackPassword(user.strip('\n'), args.threads) # this is actually gonna happen in client

    except KeyboardInterrupt as keyError:
        print(f'\nShutting Down - {repr(keyError)}')
        assert not interrupted
    except Exception as e:
        print(f'\nAn Exception Occured - {repr(e)}')
        assert not interrupted


if __name__ == '__main__':
    main()
