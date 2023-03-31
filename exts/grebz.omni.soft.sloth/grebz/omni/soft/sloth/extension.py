import omni.ext
import time
import socket
import threading


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):

        self.running = False
        self.should_continue = False
        self.udp_socket = None
        threading.Thread(target=self.udp, args=("128.235.165.151", 2390)).start()

    def on_shutdown(self):
        self.should_continue = False
        if self.udp_socket:
            # shutdown the socket if it exists
            print("shutdown socket")
            self.udp_socket.shutdown(socket.SHUT_RDWR)
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
        
        
        self.running = True
        self.should_continue = True

        while self.should_continue:

            # Send a message to the client as a byte array
            message = b"Hello UDP Client"
            self.udp_socket.sendto(message, ("10.203.195.238", port))

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