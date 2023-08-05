
In this package tamil nadu local online Fm Station


INSTALL PACKAGE

sudo apt-get install vlc

pip install tn-radio

IMPORT PACKAGE

import tn_radio\n
obj = tn_radio.Radio()

LIST OF FM STREAM

import tn_radio\n
obj = tn_radio.Radio()

obj.list_fm()

0 Ohm Namashivaya[Chennai, India]\n
1 Namakkal Thedal FM[Namakkal, India]\n
2 Natrinai FM[Tiruchirappalli, India]\n
3 Pudukkottai Thedal FM[Pudukkottai, India]\n
4 முத்தமிழ் FM மேலூர்[Melur, India]\n
5 Virudhunagar Thedal FM[Virudhunagar, India]\n

SET STREAM FM INDEX

import tn_radio\n
obj = tn_radio.Radio()\n
obj.set_stream(3)

PLAY FM 

import tn_radio\n
obj = tn_radio.Radio()\n
obj.set_stream(3)


obj.play()

STOP FM

obj.play()

PAUSE FM

obj.pause()

CHANGE FM STREAM

obj.set_stream(5)
