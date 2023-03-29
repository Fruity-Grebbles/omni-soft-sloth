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
            print("shutdown socket")
            self.udp_socket.shutdown(socket.SHUT_RDWR)
            # wait for the thread to finish
            while self.running:
                print("waiting for thread to finish")
                time.sleep(0.1)
            self.udp_socket = None

    def udp(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        max_attempts = 10
        for i in range(max_attempts):
            print("attempting to connect to server:", i)
            try:
                self.udp_socket.bind(("127.0.0.1", 20001)) 
                break
            except:
                time.sleep(1)
            if i == max_attempts:
                print("failed to connect to server")
                self.udp_socket = None
                return
        self.udp_socket.listen(1)

        print("connecting...")
        try:
            self.client_socket, self.ip_port = self.udp_socket.accept()
        except Exception as e:
            print(e)
            return
        print("client", self.ip_port, "connected")
        
        self.running = True
        self.should_continue = True
        while self.should_continue:
            bytesAddressPair = UDPServerSocket.recvfrom(1024)

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