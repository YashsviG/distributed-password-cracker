import argparse
import pickle
import multiprocessing
import socket
import time
from hmac import compare_digest as compare_hash
import crypt
from ctypes import c_wchar_p
import select


def find_algo(info_dict):
    algo_names = {
        "$y$": "yescrypt",
        "$6$": "sha256",
        "$5$": "sha512",
        "$sha1$": "sha1",
        "$2b$": "bcrypt",
        "$7$": "scrypt",
        "$md5$": "sun md5",
        "$1$": "md5crypt",
        "$_$": "bsdicrypt",
        "$$": "descrypt",
        "$3$": "nthash"
    }
    
    info_dict['algo_name'] = algo_names.get(info_dict['algo'], "unknown")
    
    if info_dict['algo'] == "$2b$":
        info_dict['salt'], info_dict['password'] = extract_bcrypt_salt(info_dict['password'])
    
    return info_dict

def extract_bcrypt_salt(password):
    # extract salt from bcrypt password hash
    salt = password[:22]
    password = password[22:]
    return salt, password



def find_password(user, count, files, length, found, stop_event, lock, passwd, cs):
    cs.setblocking(False)
    print(F"[STARING] Process_ID: {multiprocessing.current_process().pid}")
    while not found.value:
        for r in range(length[0], length[1]):
            try:
                data = cs.recv(1024).decode()
                if data == 'break':
                    print("[STOPPING]Password found by other client")
                    stop_event.set()
                    break
            except socket.error:
                pass
            line = files[r].strip()
            hashed = crypt.crypt(line, salt=user["hashed"])
            with lock:
                count.value = count.value + 1
            if compare_hash(hashed, user['hashed']):
                found.value = True
                passwd.value = line
                print(f"\n[Match Found] {user['user']}: {passwd.value}\tFound by P_ID: {multiprocessing.current_process().pid}")
                stop_event.set()
            else:
                print(f"[FAILED] {line}")


def decrypt(all_users, threads, cs):
    with open('my_file.txt', 'r') as f:
        files = f.readlines()
    num_lines = all_users[-1]['chunk'][1]-all_users[-1]['chunk'][0]
    for i in all_users[:-1]:
        start_time = time.perf_counter()
        stop_event = multiprocessing.Event()
        manager = multiprocessing.Manager()
        lock = multiprocessing.Lock()
        passwd = manager.Value(str, '')
        count = manager.Value('i', 0)
        found = manager.Value('b', False)
        find_algo(i)
        chunks = (all_users[-1]['chunk'][0], all_users[-1]['chunk'][0]+(num_lines // threads + num_lines % threads))
        process = []
        print(
                f"\n----------------------------------------------\n[WORKING ON] User: {i['user']}\tAlgorithm: {i['algo_name']}\tSalt:{i['salt']}")
        for _ in range(threads):
            p = multiprocessing.Process(target=find_password,
                                        args=(i, count, files, chunks, found, stop_event, lock, passwd, cs))
            chunks = (chunks[1], (chunks[1] + num_lines // threads))
            p.start()
            process.append(p)
        stop_event.wait()
        for p in process:
            p.terminate()

        if found.value:
            stop_time = time.perf_counter()
            cracked_passwd = passwd.value
            info = {'user': i['user'], 'passwd': cracked_passwd, 'found': True, 'time': stop_time - start_time, 'algo': i['algo_name'], 'salt': i['salt'], 'count': count.value}
            print(
                f"Time Taken: {stop_time - start_time} secs\tWords attempted: {count.value}.")
            print(f"----------------------------------------------\n")
        else:
            info = {'user': i['user'], 'found': False}
            stop_time = time.perf_counter()
            print(
                f"[Match Not Found] {i['user']}\nTime Taken: {stop_time - start_time} secs\tWords attempted: {count.value}.")
        info = pickle.dumps(info)
        cs.send(info)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=str, dest='dst_ip', required=True)
    parser.add_argument('-p', type=int, default=8000, dest='port')
    args = parser.parse_args()

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((args.dst_ip, args.port))
    info = client_socket.recv(4096)
    info = pickle.loads(info)
    decrypt(info, 6, client_socket)



if __name__ == "__main__":
    main()
