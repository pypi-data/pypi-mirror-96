# yeastarAPI
Python OOP interface for connecting to, authenticating with, and sending SMS messages via any of the 8 connected SIM cards
Currently has a class definition for incoming messages, but not implemented.

##Get started:
```
import yeastarAPI

if __name__ == '__main__':
    conn = yeastarAPI.Connection("Gateway IP", 5038, "apiuser", "apipass")
    print(yeastarAPI.SendSMS(conn, 1, "040000000", "Hello World!").Status)
```
