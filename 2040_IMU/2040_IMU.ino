/*
  WiFi UDP Send IMU data to PC

 */


#include <SPI.h>
#include <WiFiNINA.h>
#include <WiFiUdp.h>
#include <Arduino_LSM6DSOX.h>

int status = WL_IDLE_STATUS;
#include "arduino_secrets.h" 
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = SECRET_SSID;        // your network SSID (name)
char user[] = SECRET_USER;    // your network user name for WPA2 Enterprise
char pass[] = SECRET_PASS;    // your network password (use for WPA, or use as key for WEP)
int keyIndex = 0;            // your network key index number (needed only for WEP)

unsigned int localPort = 2390;      // local port to listen on

char packetBuffer[256]; //buffer to hold incoming packet
char  ReplyBuffer[1024]; // buffer to hold out

WiFiUDP Udp;

void setup() {
  //Initialize serial and wait for port to open:
  Serial.begin(9600);

  // wait 10 seconds for serial monitor to open. If it doesn't, continue anyway.
  for(int i = 0; i < 10; i++) {
    if (Serial) {
      break;
    }
    delay(1000);
  }

  // check for the WiFi module:
  if (WiFi.status() == WL_NO_MODULE) {
    try_serial_println("Communication with WiFi module failed!");
    // don't continue
    while (true);
  }

  String fv = WiFi.firmwareVersion();
  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {
    try_serial_println("Please upgrade the firmware");
  }

  // Attempt to initialize IMU
  if (!IMU.begin()) {
    try_serial_println("Failed to initialize IMU!");
    while (1);
  }


  // attempt to connect to WiFi network:
  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    try_serial_println(ssid);
    // Connect to WPA/WPA2 network. Change this line if using open or WEP network:
    status = WiFi.beginEnterprise(ssid, user, pass);

    // wait 10 seconds for connection:
    delay(10000);
  }
  try_serial_println("Connected to WiFi");
  printWifiStatus();

  try_serial_println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  Udp.begin(localPort);
}

void loop() {

  // IMU data variables
  float ax, ay, az;
  float gx, gy, gz;

  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.print("Received packet of size ");
    try_serial_println(packetSize);
    Serial.print("From ");
    IPAddress remoteIp = Udp.remoteIP();
    Serial.print(remoteIp);
    Serial.print(", port ");
    try_serial_println(Udp.remotePort());

    // read the packet into packetBufffer
    int len = Udp.read(packetBuffer, 255);
    if (len > 0) {
      packetBuffer[len] = 0;
    }
    try_serial_println("Contents:");
    try_serial_println(packetBuffer);

    // Get the IMU data
    if (IMU.accelerationAvailable()) {
      IMU.readAcceleration(ax, ay, az);
    }
    if (IMU.gyroscopeAvailable()) {
      IMU.readGyroscope(gx, gy, gz);
    }

    // Format the IMU data to send back to the PC
    sprintf(ReplyBuffer, "ax: %f, ay: %f, az: %f, gx: %f, gy: %f, gz: %f", ax, ay, az, gx, gy, gz);
    
    // Print the IMU data to the serial monitor
    try_serial_println(ReplyBuffer);

    // send a reply, to the IP address and port that sent us the packet we received
    Udp.beginPacket(Udp.remoteIP(), Udp.remotePort());
    Udp.write(ReplyBuffer);
    Udp.endPacket();
  }
}


void printWifiStatus() {
  // print the SSID of the network you're attached to:
  Serial.print("SSID: ");
  try_serial_println(WiFi.SSID());

  // print your board's IP address:
  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  try_serial_println(ip);

  // print the received signal strength:
  long rssi = WiFi.RSSI();
  Serial.print("signal strength (RSSI):");
  Serial.print(rssi);
  try_serial_println(" dBm");
}

void try_serial_println(const char *s) {
  // Try to print to serial monitor, but don't crash if it's not available.
  if (Serial) {
    Serial.println(s);
  }
}
