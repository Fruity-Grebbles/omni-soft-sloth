import omni.ext
import time
import socket
import threading


class Extension(omni.ext.IExt):
    def on_startup(self, ext_id):

        self.running = False
        self.should_continue = False
        self.tcp_socket = None
        threading.Thread(target=self.tcpip).start()

    def on_shutdown(self):
        self.should_continue = False
        if self.tcp_socket:
            print("shutdown socket")
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
            # wait for the thread to finish
            while self.running:
                print("waiting for thread to finish")
                time.sleep(0.1)
            self.tcp_socket = None

    def tcpip(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        max_attempts = 10
        for i in range(max_attempts):
            print("attempting to connect to server:", i)
            try:
                self.tcp_socket.bind(("127.0.0.1", 40005)) 
                break
            except:
                time.sleep(1)
            if i == max_attempts:
                print("failed to connect to server")
                self.tcp_socket = None
                return
        self.tcp_socket.listen(1)

        print("connecting...")
        try:
            self.client_socket, self.ip_port = self.tcp_socket.accept()
        except Exception as e:
            print(e)
            return
        print("client", self.ip_port, "connected")
        
        self.running = True
        self.should_continue = True
        while self.should_continue:
            data = self.client_socket.recv(1024)
            if not data:
                break 
            print(data)

        print("client disconnected")
        self.tcp_socket.close()
        self.tcp_socket = None
        self.running = False