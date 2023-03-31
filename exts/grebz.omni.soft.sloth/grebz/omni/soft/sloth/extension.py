import omni.ext
import time
import socket
import threading


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):

        self.running = False
        self.should_continue = False
        self.udp_socket = None
        threading.Thread(target=self.udp).start()

    def on_shutdown(self):
        self.should_continue = False
        if self.udp_socket:
            # shutdown the socket if it exists
            print("shutdown socket")
            self.udp_socket.shutdown(socket.SHUT_RDWR)
            # wait for the thread to finish
            while self.running:
                print("waiting for thread to finish")
                time.sleep(0.1)
            self.udp_socket = None

    def udp(self, ip : str, port: int, max_attempts: int = 10):
        """
        Creates a UDP socket and listens for incoming messages. We will run it
        in a thread so it doesn't block the main thread.

        Parameters
        ----------
        ip : str
            The IP address to listen on.
        port : int
            The port to listen on.
        max_attempts : int, optional
            The maximum number of attempts to connect to the server. The default is 10.
        """

        # Create a datagram (UDP) socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Attempt to bind to ip and port. Will retry for max_attempts
        for i in range(max_attempts):
            print("attempting to connect to server:", i)
            try:
                self.udp_socket.bind((ip, port)) 
                break
            except:
                time.sleep(1)
            if i == max_attempts:
                print("failed to connect to server")
                self.udp_socket = None
                return
        # Listen for incoming datagrams
        self.udp_socket.listen(1)

        print("connecting...")

        # Accept a connection
        try:
            self.client_socket, self.ip_port = self.udp_socket.accept()
        # If we get an error, print it and close the socket
        except Exception as e:
            print(e)
            return

        # Print the client's IP address
        print("client", self.ip_port, "connected")
        
        self.running = True
        self.should_continue = True

        while self.should_continue:
            bytesAddressPair = self.udp_socket.recvfrom(1024)

            message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(message)
            clientIP  = "Client IP Address:{}".format(address)
            
            print(clientMsg)
            print(clientIP)

        print("client disconnected")
        self.udp_socket.close()
        self.udp_socket = None
        self.running = False