# Distributed Password Cracker - Dictionary Attack/Brute Force
#### Ethical Distributed Password Cracker
The password cracker aims to crack passwords created using hashing algorithms:
1. Yescrypt
2. MD5crypt
3. SHA1crypt
4. SHA256crypt 
5. SHA512crypt 
6. Bcrypt
7. DEScrypt

## High Level Client-Server Architecture
<img width="621" alt="image" src="https://user-images.githubusercontent.com/45160510/236374891-1601e3a2-8c4f-4484-84b8-d04c82023f80.png">

## User Guide

Pre requisite:
- Need to have python setup on the machine.
- A shadow file to test with.
- Some file(s) containing top passwords (dictionary of passwords).

1. Run the password cracker Server: `python3 server.py -f /etc/shadow -t <#> <username>`: <br/>
&nbsp;&nbsp; &nbsp;&nbsp; <img width="318" alt="image" src="https://user-images.githubusercontent.com/45160510/236376080-18b47fd4-177e-486b-8515-61285f73a9be.png">

2. Run the password cracker Client: `python3 main.py -s <ip-address-server> -p <port>`<br/>
  &nbsp;&nbsp; &nbsp;&nbsp; - The list of the top password text file is provided in the source directory. <br/>
  &nbsp;&nbsp; &nbsp;&nbsp; - Can run it on a custom port which is different from the default one: <br/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp; <img width="578" alt="Screen Shot 2023-05-05 at 9 56 51 AM" src="https://user-images.githubusercontent.com/45160510/236377720-c1587b1a-f94c-4acf-bcca-7a47de9b7c92.png"> <br/>
3. There has been a copy of shadow file provided in source directory as well for reference. You can add some user-password lines here in this file manually and pass this to the -f flag when initiating the program instead of the /etc/shadow.


## Example Password Cracked
<img width="621" alt="image" src="https://user-images.githubusercontent.com/45160510/236375821-fa1127c9-4a9d-48f6-9bef-e3b7b482b078.png"> <img width="441" alt="image" src="https://user-images.githubusercontent.com/45160510/236376006-e99b8c81-4ede-4149-b7c7-d33475894eb5.png">



