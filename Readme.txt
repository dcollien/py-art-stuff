Uploading Micropython Firmware on ESP8266 chip:

1. Buy a "Wemos" board from aliexpress.com for ~$4

2. Install any drivers required for the usb/serial (e.g. CH34X Wemos driver) - OSX is in this repo

3. Plug it in with a microusb cable

4. pip3 install esptool

5. find out your port (OSX it's /dev/cu.wchusbserialXXXX)

6. esptool.py --port /dev/cu.wchusbserialXXXX erase_flash

7. Go to http://micropython.org/download#esp8266 and get the latest firmware

8. esptool.py --port /dev/cu.wchusbserialXXXX --baud 115200 write_flash --flash_size=detect 0 esp8266-20170108-v1.8.7.bin

(your baud rate may vary - can go faster on linux/windows, my OSX has issues)

9. screen /dev/cu.wchusbserialXXXX 115200
You're now in a python REPL, running on an ESP8266

10. Connect to wifi
>>> import network
>>> wifi = network.WLAN(network.STA_IF)
>>> wifi.active(True)
>>> wifi.connect('essid', 'password')
>>> wifi.ifconfig() # ip, mask, gateway, dns
(192.168.XXX.XXX, 255.255.255.0, 192.168.0.1, 8.8.8.8)

11. Run web repl
>>> import webrepl; webrepl.start(8266, 'password')

12. http://micropython.org/webrepl/
and enter ws://192.168.XXX.XXX:8266/ and connect

13. Upload files

Wemos Pin mappings:
D0 = 16
D1 = 5
D2 = 4
D3 = 0
D4 = 2
D5 = 14
D6 = 12
D7 = 13
D8 = 15
