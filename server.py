import argparse
import pickle
import multiprocessing
import socket

user_dict = {}

def print_stats(data):
    print(f"User:{data['user']}\tPassword:{data['passwd']}\tSalt:{data['salt']}\nAlgorithm Name:{data['algo']}\tTime Take:{data['time']}secs\tAttempts:{data['count']}")
    print("=====================================================================================\n\n")


def accept(s_socket, user_list, master_array, stop_event):
    global user_dict
    conn, addr = s_socket.accept()
    conn.setblocking(False)
    conn.send(user_list)
    my_update=0
    for i in range(len(user_list)):
        try:
            while not master_array[i]:
                try:
                    data = conn.recv(4096)
                except socket.error:
                    pass
                else:
                    if data:
                        data = pickle.loads(data)
                        if data['found']:
                            master_array[i] = 1
                            print(f"{conn.getpeername()[0]}: [FOUND] Password Found")
                            print_stats(data)
                            my_update=1
                        else:
                            print(f"{conn.getpeername()[0]}: [NOT FOUND] Password NOT Found\tUser:{data['user']}")
                        continue
            if not my_update:
                print(f"\n{conn.getpeername()[0]}: [UPDATE] Password found by another Client.")
                conn.send(b'break')
            my_update=0
        except IndexError:
            break

    stop_event.set()



    # while True:
    #     try:
    #         # print(f"{conn.getpeername()[0]}: {curr} : {master_array[curr]}: {master_array[0]}")
    #         data = conn.recv(4096)
    #         if data:
    #             data = pickle.loads(data)
    #             if data['found']:
    #                 master_array[user_dict[data['user']]] = 1
    #                 print(f"{conn.getpeername()[0]}: [FOUND] Password Found\nUser:{data['user']}\tPassword:{data['passwd']}")
    #                 curr+=1
    #             else:
    #                 print(f"{conn.getpeername()[0]}: [NOT FOUND] Password NOT Found.")
    #                 curr+=1
    #             continue
    #
    #         elif master_array[curr]:
    #             print(f"{conn.getpeername()[0]}: [UPDATE] Password found by another Client.")
    #             conn.send(b'break')
    #             curr += 1
    #
    #         print(master_array[curr] + conn.getpeername()[0])
    #         if curr >= len(user_dict):
    #             break
    #     except socket.error:
    #         pass

def extract_salt_passwd(string):
    dictionary = {}
    if string:
        split = string.split(':')
        try:
            paswd = split[1].split('$', 3)
            algo = paswd[1]
            salt = paswd[2]
            password = paswd[3]
        except IndexError:
            algo = ""
            salt = None
            password = split[1]
        dictionary = {'user': split[0], 'algo': f"${algo}$"}
        if salt is not None:
            dictionary['salt'] = salt
        else:
            pass
        dictionary['password'] = password
        dictionary['hashed'] = split[1]
    return dictionary


def extract_info(shadow_file, user_l):
    global user_dict
    all_users = []
    with open(shadow_file, 'r') as f:
        r = f.readlines()
    for e, line in enumerate(r):
        info = extract_salt_passwd(line.strip())
        if info['user'] in user_l:
            user_dict[f"{info['user']}"] = e
            all_users.append(info)
    return all_users


def data_prep(sock, nc, sf, user_l):
    with open('my_file.txt', 'r') as f:
        files = f.readlines()
    num_lines = len(files)
    chunks = (0, num_lines // nc + num_lines % nc)
    information = extract_info(sf, user_l)
    process_list=[]
    master_array = multiprocessing.Array('i', len(user_l))
    stop_event = multiprocessing.Event()
    for i in range(nc):
        chunk_dict = {'chunk': chunks}
        information.append(chunk_dict)
        info = pickle.dumps(information)
        p = multiprocessing.Process(target=accept, args=(sock, info, master_array, stop_event))
        process_list.append(p)
        information.pop()
        chunks = (chunks[1], chunks[1] + num_lines // nc)
        p.start()
    stop_event.wait()
    for p in process_list:
        p.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='shadow_file', required=True)
    parser.add_argument('-t', type=int, dest='no_of_clients', default=1)
    parser.add_argument('-p', type=int, dest='port', default=8000)
    parser.add_argument('users', nargs='+')
    args = parser.parse_args()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    server_socket.bind(('', args.port))
    server_socket.listen(args.no_of_clients)

    data_prep(server_socket, args.no_of_clients, args.shadow_file, args.users)


if __name__ == "__main__":
    main()
