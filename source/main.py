from multiprocessing import Process, Lock, Value
import multiprocessing
import utils
from hmac import compare_digest as compare_hash
from datetime import timedelta
import argparse
import time


def check_bcrypt(user_line):
    if user_line.split(":")[1].split("$", 3)[1] == "2b":
        return True
    return False

# Print information before the password is cracked
def printInformation(user, hash_name, salt, hashed_pwd):
    print("======================================================")
    print(f"User:        {user}")
    print(f"Hash Alg.:   {hash_name}")
    print(f"Salt:        {salt}")
    print(f"Hashed PWD:  {hashed_pwd}")
    print(f"PID:  {multiprocessing.current_process().pid}")

# Print information after password is cracked
def printInformation2(start, end, attempts):
    print(f"Time Taken: {str(timedelta(seconds=(end - start)))}")
    print(f"Attempts Made: {str(attempts.value)}")
    print("======================================================")


def extractShadowFileData(user_line):
    user = user_line.split(":")[0]
    try:
        hash_alg, salt, hashed_pwd = user_line.split(":")[1].split("$", 3)[1:]
        if check_bcrypt(user_line):
            salt = hashed_pwd[:22]
            hashed_pwd = hashed_pwd[23:]
    except:
        hashed_pwd = user_line.split(":")[1][3:]
        hash_alg = "0"
        salt = user_line.split(":")[1][:2]

    return {
        "user": user,
        "salt": salt,
        "hashed_pwd": hashed_pwd,
        "hash_alg": hash_alg
    }


def createProcesses(pwds, user_line, threads):
    found = Value('b', False)
    attempts = Value('i', 0)
    lock = Lock()
    chunk_size = len(pwds) // threads

    stop_event = multiprocessing.Event()

    chunks = [pwds[i: i + chunk_size] for i in range(0, len(pwds), chunk_size)]

    try:
        processes = []
        start = time.perf_counter()
        for chunk in chunks:
            process = Process(target=comparePassword, args=(
                user_line, chunk, found, attempts, lock, stop_event))

            processes.append(process)
            process.start()

        stop_event.wait()
        for process in processes:
            process.terminate()

        end = time.perf_counter()
        printInformation2(start, end, attempts)
    except Exception as e:
        print(f'\nAn Exception Occured - {repr(e)}')


def comparePassword(user_line, pwds, found, attempts, lock, stop_event):
    shadowData = extractShadowFileData(user_line)

    user = shadowData["user"]
    salt = shadowData["salt"]
    hashed_pwd = shadowData["hashed_pwd"]
    hash_alg = shadowData["hash_alg"]

    hash_name, hash_func = utils.HASH_ALGS[hash_alg]

    time.sleep(2)
    printInformation(user, hash_name, salt, hashed_pwd)

    for pwd in pwds:
        with lock:
            attempts.value = attempts.value + 1

        created_pwd = hash_func(pwd.strip(), salt=user_line.split(":")[1])

        if compare_hash(user_line.split(":")[1], created_pwd):
            found.value = True
            print(f"\nPASSWORD CRACKED! {pwd}")
            stop_event.set()


def crackPassword(user_line, threads):
    with open(utils.PASSWORD_LIST[0], mode='r') as pwd_dict:
        pwds = pwd_dict.readlines()

    createProcesses(pwds, user_line, threads)

    pwd_dict.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, dest='shadowFile', required=True)
    parser.add_argument('-t', type=int, dest='threads', default=1)
    
    parser.add_argument('users', nargs='+')
    args = parser.parse_args()

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

        for user in users_list:
            crackPassword(user.strip('\n'), args.threads)

    except KeyboardInterrupt as keyError:
        print(f'\nShutting Down - {repr(keyError)}')
        assert not interrupted
    except Exception as e:
        print(f'\nAn Exception Occured - {repr(e)}')
        assert not interrupted


if __name__ == '__main__':
    main()
