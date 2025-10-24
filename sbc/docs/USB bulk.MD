
0. Preparation
[For Linux]
■
Installation of some necessary packages.
1. Install some necessary packages below.
$ sudo apt install autoconf libtool libudev
dev gcc g++ make cmake unzip libxml2 dev
Add this command:
sudo sh
c 'echo 150 > /sys/module/usbcore/parameters/usbfs_memory_mb’
Before:
APPEND ${cbootargs} quiet
After:
APPEND ${cbootargs} usbcore.usbfs_memory_mb=150 usbcore.autosuspend=
1
[Ubuntu
(for
Change “APPEND ${cbootargs} quiet” to the command
below in the file “/boot/extlinux/extlinux.conf”.
[Raspberry Pi OS] (Legacy, Before Bullseye)
Add the command below at the end of the file “/etc/rc.local
”
before "
exit 0" to modify Bulk Transfer Rate configuration file.
■
USB setting
1. Change USB
bulk setting(1/2)
Add this parameter:
usbcore.usbfs_memory_mb
=150
[Raspberry Pi OS]
Open /boot/firmware/cmdline.
txt.
If
this file does not exist, open /boot/cmdline.txt instead.
Append
the parameter at the end of the existing single line (do not
create a new line):
Sony Corporation.
Sony Corporation.
$ cat /sys/module/usbcore/parameters/usbfs_memory_mb
$ cat /sys/module/usbcore/parameters/usbfs_memory_mb
150
150
Save
Save & Close the file and reboot. & Close the file and reboot.
Make sure that “150” is written in the configuration file.
Make sure that “150” is written in the configuration file.
“/sys/module/usbcore/parameters/usbfs_memory_mb”.
“/sys/module/usbcore/parameters/usbfs_memory_mb”.
0. Preparation
0. Preparation
[For Linux]
[For Linux]
[Ubuntu
[Ubuntu(for x86)](for x86)]
Change “quiet splash” to the command
Change “quiet splash” to the command
below in the file “/etc/default/grub” and update grub.
below in the file “/etc/default/grub” and update grub.
Before:
Before:
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash“
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash“
After:
After:
G
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.usbfs_memory_mb=150"RUB_CMDLINE_LINUX_DEFAULT="quiet splash usbcore.usbfs_memory_mb=150"
sudo update
sudo update--grubgrub
2. Reboot and check
2. Reboot and check the configurationthe configuration
■
■USB settingUSB setting
1. Change USB
1. Change USB bulk setting(2/2)bulk setting(2/2)