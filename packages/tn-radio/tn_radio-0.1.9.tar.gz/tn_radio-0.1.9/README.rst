
In this package tamil nadu local online Fm Station


INSTALL PACKAGE

sudo apt-get install vlc

pip install tn-radio

     IMPORT PACKAGE

import tn_radio

obj = tn_radio.Radio()

LIST OF FM STREAM

import tn_radio
obj = tn_radio.Radio()

obj.list_fm()

0 Ohm Namashivaya[Chennai, India]
1 Namakkal Thedal FM[Namakkal, India]
2 Natrinai FM[Tiruchirappalli, India]
3 Pudukkottai Thedal FM[Pudukkottai, India]
4 முத்தமிழ் FM மேலூர்[Melur, India]
5 Virudhunagar Thedal FM[Virudhunagar, India]

SET STREAM FM INDEX

import tn_radio
obj = tn_radio.Radio()
obj.set_stream(3)

PLAY FM 

import tn_radio
obj = tn_radio.Radio()
obj.set_stream(3)


obj.play()

STOP FM

obj.play()

PAUSE FM

obj.pause()

CHANGE FM STREAM

obj.set_stream(5)
