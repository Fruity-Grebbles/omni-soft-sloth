from omni.kit.scripting import BehaviorScript
import omni.kit.commands
from pxr import Sdf, Gf, UsdGeom
import omni.ext
import time
import socket
import threading

ADDRESS = "10.202.6.177"
PORT = 2390

class Controller(BehaviorScript):
    def on_init(self):
        self.running = False
        self.should_continue = False
        self.udp_socket = None
        threading.Thread(target=self.udp, args=(ADDRESS, PORT)).start()
        print(f"{__class__.__name__}.on_init()->{self.prim_path}")

    def on_destroy(self):
        self.should_continue = False
        if self.udp_socket:
            # shutdown the socket if it exists
            print("shutdown socket")
            self.udp_socket.shutdown(socket.SHUT_RDWR)
            self.udp_socket = None
        print(f"{__class__.__name__}.on_destroy()->{self.prim_path}")

    def on_play(self):
        self._playing = True
        print(f"{__class__.__name__}.on_play()->{self.prim_path}")

    def on_pause(self):
        self._playing = False
        print(f"{__class__.__name__}.on_pause()->{self.prim_path}")

    def on_stop(self):
        self._playing = False
        print(f"{__class__.__name__}.on_stop()->{self.prim_path}")

    def on_update(self, current_time: float, delta_time: float):

        if self._playing:

            # set the prim xform rotation to the values from the udp socket
            if self.udp_socket:
                self.prim.GetAttribute("xformOp:rotateXYZ").Set(Gf.Vec3f(0, 0, 0))

        print(f"{__class__.__name__}.on_update(current_time={current_time}, delta_time={delta_time})->{self.prim_path}")

    def udp(self, ip : str, port: int, max_attempts: int = 10):
        """
        Creates a UDP socket and listens for incoming messages. We will run it
        in a thread so it doesn't block the main thread.

        Parameters
        ----------
        ip : str
            The IP address to send to.
        port : int
            The port of the remote device.
        max_attempts : int, optional
            The maximum number of attempts to connect to the server. The default is 10.
        """

        # Create a datagram (UDP) socket
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        hostname=socket.gethostname()
        IPAddr=socket.gethostbyname(hostname)

        # Attempt to bind to ip and port. Will retry for max_attempts
        for i in range(max_attempts):
            print("attempting to connect to server:", i)
            try:
                self.udp_socket.bind((IPAddr, 2380)) 
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
            self.udp_socket.sendto(message, (ip, port))

            bytesAddressPair = self.udp_socket.recvfrom(1024)

            self.message = bytesAddressPair[0]

            address = bytesAddressPair[1]

            clientMsg = "Message from Client:{}".format(self.message)
            clientIP  = "Client IP Address:{}".format(address)
            
            print(clientMsg)
            print(clientIP)

        print("client disconnected")
        self.udp_socket.close()
        self.udp_socket = None
        self.running = False
