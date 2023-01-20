
This module contains two functions, `send_with_size` and `recv_by_size` for sending and receiving data over a socket. It also has several constants for configuring the data transfer. 

The `send_with_size` function takes a socket and a byte data as parameters and sends it over the socket. It also adds a header containing the length of the data which is used by the `recv_by_size` function to read the data.

The `recv_by_size` function takes a socket as a parameter and reads data from it. It reads the header containing the length of the data first and then reads the data. It returns the data as a byte array.