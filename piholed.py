# Pi-hOLED

import json
import subprocess
import time
import socket
import psutil
import requests
# Import Blinka
from board import SCL, SDA
import busio
import adafruit_ssd1306
# Import Python Imaging Library
from PIL import Image, ImageDraw, ImageFont

api_url = 'http://localhost/admin/api.php'

WIDTH = 128
HEIGHT = 32
BORDER = 0
DURATION = 5

def get_cpu_temp():
    tmp = open('/sys/class/thermal/thermal_zone0/temp')
    cpu = tmp.read()
    tmp.close()
    cpu_temp = '{:.2f}'.format( float(cpu)/1000 ) + "° C"
    return cpu_temp

def get_cpu_speed(): # get the CPU speed 
    tmp1 = open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq")
    freq = tmp1.read
    cpu_speed = ('%u MHz' % (int(freq()) / 1000))
    return cpu_speed

def get_cpu_load(): # get the CPU load %
    cmd = "top -bn1 | grep load | awk '{printf \" %.2f\", $(NF-2)}'"
    cpu_load = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return cpu_load + " %"

def get_cpu_mem(): # get the memory usage
    cmd = "free -m | awk 'NR==2{printf \"Mem: %s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
    cpu_mem = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return cpu_mem

def clear_display():
    # Draw a white background
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    # Draw a smaller inner rectangle
    draw.rectangle((BORDER, BORDER, oled.width - BORDER - 1, oled.height - BORDER - 1), outline=0, fill=0)

def display_screen_cpu():
    for i in range(DURATION):
        clear_display()
        # Define the content to be displayed
        text = "CPU Temp: " + get_cpu_temp()
        draw.text((0,0), 
            text, font=font, fill=255)
        text = "CPU Speed: " + get_cpu_speed()
        draw.text((0,10), 
            text, font=font, fill=255)
        text = "CPU Load: " + get_cpu_load()
        draw.text((0,20), 
            text, font=font, fill=255)
        text = get_cpu_mem()
        draw.text((0,30), 
            text, font=font, fill=255)
    
    # Draw the display
    oled.image(image)
    oled.show()
    time.sleep(1)

def display_screen_pihole():
    for i in range(DURATION):
        clear_display()
        try:
            r = requests.get(api_url)
            data = json.loads(r.text)
            DNSQUERIES = data['dns_queries_today']
            ADSBLOCKED = data['ads_blocked_today']
            CLIENTS = data['unique_clients']
        except KeyError:
            time.sleep(1)
            continue
 
    draw.text((x, top), "IP: " + str(IP) +
              " (" + HOST + ")", font=font, fill=255)
    draw.text((x, top + 8), "Ads Blocked: " +
              str(ADSBLOCKED), font=font, fill=255)
    draw.text((x, top + 16), "Clients:     " +
              str(CLIENTS), font=font, fill=255)
    draw.text((x, top + 24), "DNS Queries: " +
              str(DNSQUERIES), font=font, fill=255)
    
    # Draw the display
    oled.image(image)
    oled.show()
    time.sleep(1)

# Create the I2C interface.
i2c = busio.I2C(SCL, SDA)

# Create the SSD1306 OLED class.
# The first two parameters are the pixel width and pixel height.  Change these
# to the right size for your display!
oled = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c, addr=0x3c)

# Load fonts.
font = ImageFont.truetype("OpenSans-Bold.ttf", 8)

# Define an image using 1-bit color
image = Image.new('1', (oled.width, oled.height))
# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

print("Running - press CTRL-C to quit")

try:
    while True:
        display_screen_cpu()
        display_screen_pihole()

except KeyboardInterrupt:
    draw.rectangle((0, 0, oled.width, oled.height), outline=255, fill=255)
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)
    oled.image(image)
    oled.show()

print("Bye..........")

