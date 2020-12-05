set backupFilename=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%
esptool.py --port COM%1 --baud 460800 read_flash 0x00000 0x400000 dump_%DATE%.img