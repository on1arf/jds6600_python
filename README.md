jds6600_python:

Python class to remote-control a Junce-Instrument JDS6600 signal generator, using the USB-connection (serial-line emulation)

version 0.0.1 (2018/01/19): initial release, reading basic parameters


API-calls:

*** API information functions:

getAPIversion()
	returns verion of the API (currently 1)

getAPIrelease()
	returns release of the API (currently "0.0.1 2018-01-19")


*** creating the object:
	from jds6800 import jds6600
	myjds6600 = jds6600("/dev/ttyUSB3")



*** Device information functions:

getwaveformlist()
	returns list of all available waveforms on the device

getdevicetype()
	returns the devicetype (MHz) of the device

getserialnumber()
	returns the serial number of the device




*** reading Device and channel Status:

getchannelenable()
	returns the status of the channel-enable information of both channels

getwaveform(channel)
	returns the currently selected waveform of a channel

getfrequency(channel)
	returns the current frequency of a channel

getfrequency_m(channel)
	returns the current frequency and multiplier of a channel

getamplitude(channel)
	returns the amplitude of a channel

getoffset(channel)
	returns the offset of a channel

getdutycycle(channel)
	returns the dutycycle of a channel

getphase()
	returns the phase-setting of the channel-2


*** writing device and channel information

setchannelenable(channel1,channel2)
	sets channel-enable of both channels.

setwaveform(channel,waveform-id)
setwaveform(channel,waveform-name)
	sets waveform for a channel, either using waveform-id (numeric) or
	waveform-name (text)

setfrequency(channel,frequency)
	sets the frequency of a channel
	Maximum Frequency: 60 MHz
	resolution: 0.01 Hz

setfrequency_m(channel,frequency,multiplier)
	sets the frequency and frequenct-multiplier of a channel
	Maximum Frequency:
		60 Mhz for multiplier-setting 0, 1 and 2
		80 Khz for multiplier-setting 3
		80 Hz for multiplier-setting 4
	resolution:
		0.01 Hz for multiplier-setting 0, 1 and 2
		0.00001 Hz for multiplier-setting 3
		0.00000001 Hz for multiplier-setting 4

setamplitude(channel,amplitude)
	sets the amplitude of a channel

setoffset(channel,offset)
	sets the offset of a channel

setduttycycle(channel,dutycycle)
	sets the dutycycle of a channel

setphase(phase)
	sets the phase of channel 2 vs. channel 1



*** Examples


from jds6600 import jds6600

jds6600.getAPIversion()
jds6600.getAPIrelease()

j = jds6600("/dev/ttyUSB3")

j.getwaveformlist()

j.getdevicetype()
j.getserialnumber()
j.getchannelenable()

for ch in (1,2):
	j.getwaveform(ch)
	j.getfrequency(ch)
	j.getamplitude(ch)
	j.getoffset(ch)
	j.getdutycycle(ch)

j.getphase()


j.setfrequency(1,1000)
j.setfrequency_m(1,40000,1)

j.setwaveform(2,2)
j.setwaveform(1,"sinc")



ENJOY!!!


Kristoff (ON1ARF)
