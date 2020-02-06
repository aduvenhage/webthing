

Pi image
=============
- diskutil list
- diskutil unmountDisk /dev/diskX
- sudo dd bs=1m if=~/Downloads/2017-11-29-raspbian-stretch-lite.img of=/dev/rdisk2 conv=sync


Pi headless setup
=============
- copy ssh file into SD boot root to enable SSH server
- update and copy wpa_supplicant.conf file into boot root to setup WiFi
- enable UART on RPi3 by adding 'enable_uart=1' to config.txt

- interact through serial port: screen /dev/tty.usbserial-AH03FKF5 115200


Misc Pi Setup:
===========
- swap file: configure config file '/var/swap'
- change hostname: sudo nano /etc/hostname; sudo nano /etc/hosts 
- enable v4l picam driver: sudo modprobe bcm2835-v4l2
- enable v4l picam driver always on startup: edit /etc/modules (i.e. 'sudo nano /etc/modules') and add 'bcm2835-v4l2'
- turn off HDMI: add `/usr/bin/tvservice -o` to `/etc/rc.local` file


Python3 Setup:
==============
- sudo apt install virtualenv
- sudo apt install python3-pip
- sudo apt install python3-picamera
- virtualenv -p python3 venv
- pip install picamera


Hamachi Setup (Pi2/3):
=================
- sudo apt-get update
- sudo apt-get install --fix-missing lsb lsb-core
- sudo wget https://www.vpn.net/installers/logmein-hamachi_2.1.0.198-1_armhf.deb
- sudo dpkg -i logmein-hamachi_2.1.0.198-1_armhf.deb
- sudo hamachi login
- sudo hamachi do-join <NETWORK_ID>


Hamachi Setup (Pi Zero):
===================
** note: uses 'el' architecture install and FORCES it (it works!!)

- sudo apt-get update
- sudo apt-get install --fix-missing lsb lsb-core
- sudo wget https://www.vpn.net/installers/logmein-hamachi_2.1.0.198-1_armel.deb
- sudo dpkg --force-architecture --force-depends -i logmein-hamachi_2.1.0.198-1_armel.deb
- sudo hamachi login
- sudo hamachi do-join <NETWORK_ID>




Static IP Setup
===========
- edit config file: nano /etc/dhcpcd.conf
- uncomment / update static IP details

```
# Example static IP configuration:
interface wlan0
static ip_address=192.168.8.10/24
static routers=192.168.8.1
static domain_name_servers=192.168.8.1 8.8.8.8
```


PI Web Cam
=========
- https://elinux.org/RPi-Cam-Web-Interface
- sudo apt-get update
- sudo apt-get dist-upgrade
- git clone https://github.com/silvanmelchior/RPi_Cam_Web_Interface.git
- cd RPi_Cam_Web_Interface
- ./install.sh

- edit config file: nano /etc/apache2/sites-available/raspicam.conf (change 'DocumentRoot /var/www' to 'DocumentRoot /var/www/html')


Pi file sharing
==========
- http://raspberrypituts.com/access-raspberry-pi-files-in-your-os-x-finder/
- open afp://146.64.217.141 in OSx terminal

- copy file from pi: scp pi@192.168.8.111:foo.jpg .
- copy file to pi: scp foo.jpg pi@192.168.8.111:


Pi OLED setup
===========
- enable PI I2C with raspi-config
- test I2C device connection: i2cdetect -y 1

- sudo apt-get install build-essential python-dev python-pip
- sudo pip install RPi.GPIO

- sudo apt-get install python-imaging python-smbus i2c-tools

- git clone https://github.com/adafruit/Adafruit_Python_SSD1306.git
- cd Adafruit_Python_SSD1306
- sudo python setup.py install


Pi startup
===========
- update '/etc/rc.local' with the following, before exit(0):
su pi -c '/home/pi/startup.sh&'

This runs the script 'startup.sh' as the pi user.

-or just:
/home/pi/startup.sh &

to run as root

- Also, update startup.sh and copy to pi home folder.
- make startup script executable with: chmod u+x startup.sh



OpenCV setup:
===========

- git clone https://github.com/opencv/opencv.git
- use ccmake (cmake-curses-gui) to setup build
  (might need to install some dependencies)

- make
- make install

Example:
- https://github.com/BVLC/caffe/wiki/OpenCV-3.3-Installation-Guide-on-Ubuntu-16.04




OpenCV (CV2) install:
=====================

- sudo apt install libatlas3-base libwebp6 libtiff5 libjasper1 libilmbase23 libopenexr23 libavcodec58 libavformat58 libavutil56 libswscale5 libgtk-3-0 libpangocairo-1.0-0 libpango-1.0-0 libatk1.0-0 libcairo-gobject2 libcairo2 libgdk-pixbuf2.0-0 

- pip install opencv-python-headless
- pip install opencv-contrib-python-headless









