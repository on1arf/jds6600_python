# example application to read and change the status of a JDS6600
# connected over USB

# version 0.1 - 20180126
# version 0.2 - 20191007

# kristoff Bonne (ON1ARF)

# import library
from jds6600 import jds6600

j = jds6600("/dev/ttyUSB3")

j.getAPIinfo_version()
j.getAPIinfo_release()



# API information calls
j.getinfo_devicetype()
j.getinfo_serialnumber()

j.getinfo_waveformlist()


# get status of jds6600
j.getchannelenable()

for ch in (1,2):
	j.getwaveform(ch)
	j.getfrequency(ch)
	j.getamplitude(ch)
	j.getoffset(ch)
	j.getdutycycle(ch)

j.getphase()


# changing status
j.setfrequency(1,1000)
j.setfrequency(1,40000,1)

j.setwaveform(2,2)
j.setwaveform(1,"sinc")

