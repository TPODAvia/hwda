I2C -> sensor module

GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) #red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) #green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) #blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) #red alarm led

pip3 install RPi.bme280

sudo apt update
sudo apt install -y i2c-tools
pi@raspberrypi:~/hwda/2 Second Project – Spying Eye $ i2cdetect -y 1
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- 68 -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- 76 -- 