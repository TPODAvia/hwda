readChId = 2813576;  % ID of first channel
writeChId = 2813583; % ID of second channel
readKey = 'K89KZSGUZN6N0A9L';
writeKey = '82FLGKRS14NIVP5Z';

[pressure,time] = thingSpeakRead(readChId, 'Fields',3, 'NumPoints',1, 'ReadKey',readKey);

% disp(pressure);

LEVEL_1 = 767.2;  % mmHg
LEVEL_2 = 756.92; % mmHg
if (pressure >= LEVEL_1)
    text="The weather will be stable";
elseif (pressure >= LEVEL_2 && pressure <= LEVEL_1)
    text="The weather will be cloudy";
else
    text="The weather will be rainy";
end

thingSpeakWrite(writeChId,'Fields',1,'TimeStamps',time,'Values',text,'Writekey',writeKey);
disp(text);