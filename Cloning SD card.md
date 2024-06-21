# SD card Cloning

If you haven't got the img file, read the SD Card disk to the img file using this command

``` bash
sudo dd if=/dev/sdX of=/path/to/your/image.img bs=4M status=progress
```
change the "if=/dev/sdX" to the path of the SD Card and change "the of=/path/to/your/image.img"

If you already have the img file that was read from the SD Card, you can clone the img file to the other SD Card

``` bash
sudo dd if=/path/to/your/image.img of=/dev/sdX bs=4M status=progress
```
