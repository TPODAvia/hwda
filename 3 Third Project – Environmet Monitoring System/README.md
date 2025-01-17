I2C -> sensor module

GPIO.setup(31, GPIO.OUT, initial=GPIO.LOW) #red led
GPIO.setup(35, GPIO.OUT, initial=GPIO.LOW) #green led
GPIO.setup(37, GPIO.OUT, initial=GPIO.LOW) #blue led
GPIO.setup(29, GPIO.OUT, initial=GPIO.LOW) #red alarm led