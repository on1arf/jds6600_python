# jds6600.py
# library to remote-control a JDS6600 signal generator

# Kristoff Bonne (C)
# published as open-source (license te be added later)

# Revisions:
# Version 0.0.1: 2018/01/19: initial release, reading basic parameters
# version 0.0.2: 2018/01/28: added "measure" menu + support functions, documentation
# version 0.0.3: 2018/02/07: added "counter" and "sweep" menu


import serial
import binascii


###########
#  Errors #
###########

class UnknownChannelError(ValueError):
	pass

class UnexpectedValueError(ValueError):
	pass

class UnexpectedReplyError(ValueError):
	pass

class FormatError(ValueError):
	pass

class WrongMode(RuntimeError):
	# called when commands are issued with the jds6600 not in the correct
	# mode
	pass


#################
# JDS6600 class #
#################

class jds6600:
	'jds6600 top-level class'

	# serial device (opened during object init))
	ser = None

	# commands
	DEVICETYPE=0
	SERIALNUMBER=1
	CHANNELENABLE=20
	WAVEFORM1=21
	WAVEFORM2=22
	FREQUENCY1=23
	FREQUENCY2=24
	AMPLITUDE1=25
	AMPLITUDE2=26
	OFFSET1=27
	OFFSET2=28
	DUTYCYCLE1=29
	DUTYCYCLE2=30
	PHASE=31
	ACTION=32
	MODE=33

	MEASURE_COUP=36 # coupling (AC or DC)
	MEASURE_GATE=37 # gatetime
	MEASURE_MODE=38 # mode (Freq or Periode)

	COUNTER_COUPL=MEASURE_COUP
	COUNTER_RESETCOUNTER=39

	SWEEP_STARTFREQ=40
	SWEEP_ENDFREQ=41
	SWEEP_TIME=42
	SWEEP_DIRECTION=43
	SWEEP_MODE=44 # mode: linair or Log
	
	COUNTER_DATA_COUNTER=80
	MEASURE_DATA_FREQ_LOWRES=81 # low resolution freq counter, used for mode "frequency"
	MEASURE_DATA_FREQ_HIGHRES=82 # high resolution freq. counter, usef for mode "period". UI: valid up to 2 Khz
	MEASURE_DATA_PW1=83
	MEASURE_DATA_PW0=84
	MEASURE_DATA_PERIOD=85
	MEASURE_DATA_DUTYCYCLE=86
	MEASURE_DATA_U1=87
	MEASURE_DATA_U2=88
	MEASURE_DATA_U3=89




	# waveforms: registers 21 (ch1) and 22 (ch2))
	# 0 to 16: predefined waveforms
	wave=("SINE","SQUARE","PULSE","TRIANGLE","PARTIALSINE","CMOS","DC","HALF-WAVE","FULL-WAVE","POS-LADDER","NEG-LADDER", "NOISE", "EXP-RIZE","EXP-DECAY","MULTI-TONE","SINC","LORENZ")
	# 101 to 160: arbitary waveforms
	awave=[]
	for a in range(1,61):
		if a < 9:
			awave.append("ARBITRARY0"+str(a))
		else:
			awave.append("ARBITRARY"+str(a))
	# end for
		

	# modes: register 33
	# note: use lowest 4 bits for wrting
	# note: use highest 4 bits for reading
	modes = ((0,"WAVE_CH1"),(0,"WAVE_CH1"),(1,"WAVE_CH2"),(1,"WAVE_CH2"),(2,"SYSTEM"),(2,"SYSTEM"),(-1,""),(-1,""),(4,"MEASURE"),(5,"COUNTER"),(6,"SWEEP_CH1"),(7,"SWEEP_CH2"),(8,"PULSE"),(9,"BURST"))

	# action: register 32
	actionlist=(("STOP","0,0,0,0"),("COUNT","1,0,0,0"),("SWEEP","0,1,0,0"),("PULSE","1,0,1,1"),("BURST","1,0,0,1"))
	action={}
	for (actionname,actioncode) in actionlist:
		action[actionname]=actioncode
	# end for

	
	# measure mode parameters
	measure_coupling=("AC(EXT.IN)","DC(EXT.IN)")
	measure_mode=("M.FREQ","M.PERIOD")


	# sweep parameter
	sweep_direction=("RISE","FALL","RISE&FALL")
	sweep_mode=("LINEAR","LOGARITHM")


	# frequency multiplier
	freqmultiply=(1,1,1,1/1000,1/1000000)

	###############
	# oonstructor #
	###############

	def __init__(self,fname):
			jds6600.ser = serial.Serial(
				port= fname,
				baudrate=115200,
				parity=serial.PARITY_NONE,
				stopbits=serial.STOPBITS_ONE,
				bytesize=serial.EIGHTBITS,
				timeout=1		)
	# end constructor



	#####################
	# support functions #
	#####################

	#####
	# low-level support function

	# parse data from read command
	def __parsedata(self,cmd,data):
		try:
			(one,two)=data.split("=")
		except ValueError:
			raise FormatError("Parsing Returned data: Invalid format, missing \"=\"")
	
		two_b=two.split(".")

		if len(two_b) < 2:
			raise FormatError("Parsing Returned data: Invalid format, missing \".\"")

		if len(two_b) > 2:
			raise FormatError("Parsing Returned data: Invalid format, too many \".\"")

		# check if returned data matches cmd that was send
		if cmd != None:
			if one != ":r"+cmd:
				raise FormatError("Parsing Return data: send/received cmd mismatch: "+data)
			# end if
		# end if

		# done: return data: part between "=" and ".", split on ","
		return two_b[0].split(",")
	# end __parsedata

	# command in textual form
	def __cmd2txt(self,cmd):
		if cmd < 10:
			return "0"+str(cmd)
		else:
			return str(cmd)
		# end if
	# end cmd2txt

	# create command in textual form for a particular channel, 
	def __cmd2txt_ch(self,ch,cmd1,cmd2):
		if ch == 1:
			return self.__cmd2txt(cmd1)
		elif ch == 2:
			return self.__cmd2txt(cmd2)
		else:
			raise UnknownChannelError(channel)
		# end if - elsif - else
	# end cmd2text per channel

	# send read command (for 1 datapoint)
	def __sendreadcmd(self,cmd):
		if self.ser.is_open == True:
			tc=":r"+cmd+"=0."+chr(0x0a)
			self.ser.write(tc.encode())
	# end __sendreadcmd

	# send read command (for n datapoint)
	def __sendreadcmd_n(self,cmd,n):
		if (n < 1):
			raise ValueError(n)

		# "n" in command start with 0 for 1 read-request
		n -= 1

		if self.ser.is_open == True:
			tc=":r"+cmd+"="+str(n)+"."+chr(0x0a)
			self.ser.write(tc.encode())
	# end __sendreadcmd_n

	# get responds of read-request and parse (1 read)
	def __getrespondsandparse(self,cmd):
		# get one line responds from serial device
		ret=self.ser.readline()
		# convert bytearray into string, then strip off terminating \n and \r
		ret=str(ret,'utf-8').rstrip()

		return self.__parsedata(cmd,ret)
	# end __get responds and parse 1


	# get responds of read-request and parsre ("n" read)
	def __getrespondsandparse_n(self,cmd, n):

		ret=[] # return value

		c = int(cmd) # counter
		for l in range(n):
			# get one line responds from serial device
			retserial=self.ser.readline()
			# convert bytearray into string, then strip off terminating \n and \r
			retserial=str(retserial,'utf-8').rstrip()


			# get parsed data
			# assume all data are single-value fields
			(parseddata,)=self.__parsedata(str(c),retserial)

			ret.append(parseddata)

			# increase next expected to-receive data
			c += 1
		# end for

		# return parsed data

		return ret
	# end __get responds and parse 1



	
	# send write command and wait for "ok"
	def __sendwritecmd(self,cmd, val):
		if self.ser.is_open == True:
			if type(val) == int:
				val = str(val)
			tc=":w"+cmd+"="+val+"."+chr(0x0a)
			self.ser.write(tc.encode())

			# wait for "ok"

			# get one line responds from serial device
			ret=self.ser.readline()
			# convert bytearray into string, then strip off terminating \n and \r
			ret=str(ret,'utf-8').rstrip()

			if ret != ":ok":
				raise UnexpectedReplyError(ret)
			# end if

		#end if
	# end __sendreadcmd


	#####
	# high-level support function

	# set action
	def __setaction(self,action):
		# type check
		if type(action) != str:
			raise TypeError(action)
		# end if

		try:
			cmd=self.__cmd2txt(jds6600.ACTION)
			self.__sendwritecmd(cmd,jds6600.action[action])
		except KeyError:
			errmsg="Unknown Action: "+action
			raise ValueError(errmsg)
		# end try

	# end set action

	###################
	# DEBUG functions #
	###################

	def DEBUG_readregister(self,register,count):
		if self.ser.is_open == True:
			regtxt=self.__cmd2txt(register)
			tc=":r"+regtxt+"="+str(count)+"."+chr(0x0a)
			self.ser.write(tc.encode())

			ret=self.ser.readline()
			while ret != b'':
				print(str(ret))
				ret=self.ser.readline()
			# end while 
		# end if
	# end readregister
		
	def DEBUG_writeregister(self,register,value):
		if self.ser.is_open == True:
			regtxt=self.__cmd2txt(register)
			if type(value) == int:
				value=str(value)

			tc=":w"+regtxt+"="+value+"."+chr(0x0a)
			self.ser.write(tc.encode())

			ret=self.ser.readline()
			while ret != b'':
				print(str(ret))
				ret=self.ser.readline()
			# end while 
		# end if

	# end write register


	##############
	# PUBLIC API #
	##############

	#########################
	# Part 0: API information

	
	# API version
	def getinfo_APIversion():
		return 0
	# end getAPIversion

	# API release number
	def getinfo_APIrelease():
		return "0.0.2 2018-01-24"
	# end get API release


	#############################
	# Part 1: information queries

	# list of waveforms
	def getinfo_waveformlist(self):
		waveformlist=[]

		count=0
		for w in jds6600.wave:
			waveformlist.append((count,w))
			count += 1
		# end for

		count=101
		for a in jds6600.awave:
			waveformlist.append((count,a))
			count += 1
		# end for

		return waveformlist
	# end get waveform list



	# get list of modes
	def getinfo_modelist(self):
		modelist=[]

		lastmode=-1

		# create list of modes, removing dups
		for (modeid,modetxt) in jds6600.modes:
			# ignore modes with modeid < 0 (not used)
			if modeid < 0:
				continue
			# end if

			if modeid != lastmode:
				modelist.append((modeid,modetxt))
				lastmode = modeid
			# end if
		# end for

		return modelist
	# end getinfo modelist


	##################################
	# Part 2: reading basic parameters

	# get device type
	def getdevicetype(self):
		cmd=self.__cmd2txt(jds6600.DEVICETYPE)
		self.__sendreadcmd(cmd)

		(devicetype,)=self.__getrespondsandparse(cmd)
		return int(devicetype)
	# end get device type


	# get serial number
	def getserialnumber(self):
		cmd=self.__cmd2txt(jds6600.SERIALNUMBER)
		self.__sendreadcmd(cmd)

		(sn,)=self.__getrespondsandparse(cmd)
		return int(sn)
	# end get serial number


	# get channel enable status
	def getchannelenable(self):
		cmd=self.__cmd2txt(jds6600.CHANNELENABLE)
		self.__sendreadcmd(cmd)

		(ch1,ch2)=self.__getrespondsandparse(cmd)
		if ch1 == "1":
			ch1=True
		else:
			ch1=False

		if ch2 == "1":
			ch2=True
		else:
			ch2=False

		return(ch1,ch2)
	# end get channel enable status

	# get waveform
	def getwaveform(self, channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.WAVEFORM1,jds6600.WAVEFORM2)

		self.__sendreadcmd(cmd)
		(waveform,)=self.__getrespondsandparse(cmd)
		waveform=int(waveform)

		# waveform 0 to 16 are in "wave" list, 101 to 160 are in awave
		try:
			return (waveform,jds6600.wave[waveform])
		except IndexError:
			pass

		try:
			return (waveform,jds6600.awave[waveform-101])
		except IndexError:
			raise UnexpectedValueError(waveform)
	# end getwaveform

	# get frequency _with multiplier
	def getfrequency_m(self,channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.FREQUENCY1,jds6600.FREQUENCY2)

		self.__sendreadcmd(cmd)
		(f1,f2)=self.__getrespondsandparse(cmd)
		(f1,f2)=(int(f1),int(f2))

		# parse multiplier (value after ",")
		# 0=Hz, 1=KHz,2=MHz, 3=mHz,4=uHz)
		# note f1 is frequency / 100
		try:
			return((f1/100*self.freqmultiply[f2],f2))
		except IndexError:
			# unexptected value of frequency multiplier
			raise UnexpectedValueError(f2)
		# end elsif
	# end function getfreq

	# get frequency _no multiplier information
	def getfrequency(self,channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.FREQUENCY1,jds6600.FREQUENCY2)

		self.__sendreadcmd(cmd)
		(f1,f2)=self.__getrespondsandparse(cmd)
		(f1,f2)=(int(f1),int(f2))

		# parse multiplier (value after ","): 0=Hz, 1=KHz,2=MHz, 3=mHz,4=uHz)
		# note1: frequency unit is Hz / 100
		# note2: multiplier 1 (khz) and 2 (mhz) only changes the visualisation on the
		#							display of the jfs6600. The frequency itself is calculated in
		#							the same way as for multiplier 0 (Hz)
		#			mulitpliers 3 (mHZ) and 4 (uHz) do change the calculation of the frequency
		try:
			return(f1/100*self.freqmultiply[f2])
		except IndexError:
			# unexptected value of frequency multiplier
			raise UnexpectedValueError(f2)
		# end elsif
	# end function getfreq


	# get amplitude
	def getamplitude(self, channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.AMPLITUDE1,jds6600.AMPLITUDE2)

		self.__sendreadcmd(cmd)
		(amplitude,)=self.__getrespondsandparse(cmd)
		amplitude=int(amplitude)

		# amplitude is mV -> so divide by 1000
		return amplitude/1000
	# end getamplitude
	
	
	# get offset
	def getoffset(self, channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.OFFSET1,jds6600.OFFSET2)

		self.__sendreadcmd(cmd)
		(offset,)=self.__getrespondsandparse(cmd)
		offset=int(offset)

		# offset unit is 10 mV, and then add 1000
		return (offset-1000)/100
	# end getoffset

	# get dutcycle
	def getdutycycle(self, channel):
		if type(channel) != int:
			raise TypeError(channel)

		cmd=self.__cmd2txt_ch(channel,jds6600.DUTYCYCLE1,jds6600.DUTYCYCLE2)

		self.__sendreadcmd(cmd)
		(dutycycle,)=self.__getrespondsandparse(cmd)
		dutycycle=int(dutycycle)

		# dutycycle unit is 0.1 %, so divide by 10
		return dutycycle/10
	# end getdutycycle

	
	# get phase
	def getphase(self):
		cmd=self.__cmd2txt(jds6600.PHASE)

		self.__sendreadcmd(cmd)
		(phase,)=self.__getrespondsandparse(cmd)
		phase=int(phase)

		# phase unit is 0.1 degrees, so divide by 10
		return phase/10
	# end getphase

	
	##################################
	# Part 3: writing basic parameters


	# set channel enable
	def setchannelenable(self,ch1,ch2):
		if type(ch1) != bool:
			raise TypeError(ch1)
		if type(ch2) != bool:
			raise TypeError(ch1)

		enable=""
		# channel 1
		if ch1 == True:
			enable += "1"
		else:
			enable += "0"
		# end else - if

		if ch2 == True:
			enable += ",1"
		else:
			enable += ",0"
		# end else - if

		# write command
		cmd=self.__cmd2txt(jds6600.CHANNELENABLE)
		self.__sendwritecmd(cmd,enable)
	# end set channel enable

	# set waveform
	def setwaveform(self,channel,waveform):
		if type(channel) != int:
			raise TypeError(channel)
		if (type(waveform) != int) and (type(waveform) != str):
			raise TypeError(waveform)

		# wzveform can be integer or string
		w=None

		if type(waveform) == int:
			# waveform is an integer
			if waveform < 101:
				try:
					jds6600.wave[waveform]
				except IndexError:
					raise ValueError(waveform)
				# end try

			else:
				try:
					jds6600.awave[waveform-101]
				except IndexError:
					raise ValueError(waveform)
				# end try
			# end if

			# ok, it exists!
			w=waveform

		else:
			# waveform is a string

			# check all waeform descriptions in wave and awave
			count=0
			for l in jds6600.wave:
				if waveform.upper() == l:
					# requested waveformname matches name in "wave" list
					w=count
					break
				# end if
				count += 1
			# end for

			# not in "wave" list -> check "awave" list
			if w == None:
				count=101 # waveform number is index-in-awave list + 101
				for l in jds6600.awave:
					if waveform.upper() == l:
						# requested waveformname matches name in "awave" list
						w=count # waveform number is index-in-awave list + 101
						break
					# end if
					count += 1
				# end for
			# end if

			# still not found?, -> error
			if w == None:
				raise ValueError(waveform)
		# ens else - elsif - if


		cmd=self.__cmd2txt_ch(channel,jds6600.WAVEFORM1,jds6600.WAVEFORM2)
		self.__sendwritecmd(cmd,w)

	# end function set waveform


	# set frequency (with multiplier)
	def setfrequency(self,channel,freq,multiplier=0):
		if type(channel) != int:
			raise TypeError(channel)
		if (type(freq) != int) and (type(freq) != float):
			raise TypeError(freq)
		if type(multiplier) != int:
			raise TypeError(multiplier)



		if (freq < 0):
			raise ValueError(freq)

		# do not execute set-frequency when the device is in sweepfrequency mode
		currentmode=self.getmode()

		if (channel == 1) and (currentmode[1] == "SWEEP_CH1"):
		# for channel 1
			raise WrongMode()
		elif (channel == 2) and (currentmode[1] == "SWEEP_CH2"):
		# for channel 2
			raise WrongMode()
		# end elsif - if


			
		# freqmultier should be one of the "frequency multiply" values
		try:
			self.freqmultiply[multiplier]
		except IndexError:
			raise ValueError[multiplier]

		# frequency limit:
		#		60 Mhz for multiplier 0 (Hz), 1 (KHz) and 2 (MHz)
		#		80 Khz for multiplier 3 (mHz) 
		#		80  Hz for multiplier 4 (uHz)
		# trying to configure a higher value can result in incorrect frequencies

		if multiplier < 3:
			if freq > 60000000:
				raise ValueError(freq)
			# end if
		elif multiplier == 3:
			if freq > 80000:
				raise ValueError(freq)
			# end if
		else: # multiplier == 4
			if freq > 80:
				raise ValueError(freq)
			# end if
		# end else - elsif - if

				

		# round to nearest 0.01 value
		freq=int(freq*100/jds6600.freqmultiply[multiplier]+0.5)
		
		cmd=self.__cmd2txt_ch(channel,jds6600.FREQUENCY1,jds6600.FREQUENCY2)

		value=str(freq)+","+str(multiplier)
		self.__sendwritecmd(cmd,value)
	# end set frequency (with multiplier)


	# set amplitude
	def setamplitude(self, channel, amplitude):
		if type(channel) != int:
			raise TypeError(channel)
		if (type(amplitude) != int) and (type(amplitude) != str):
			raise TypeError(amplitude)


		# amplitude is between 0 and 20 V
		if (amplitude < 0) or (amplitude > 20):
			raise ValueError(amplitude)

		# round to nearest 0.001 value
		amplitude=int(amplitude*1000+0.5)
		
		cmd=self.__cmd2txt_ch(channel,jds6600.AMPLITUDE1,jds6600.AMPLITUDE2)

		self.__sendwritecmd(cmd,amplitude)
	# end setamplitude
	
	

	# set offset
	def setoffset(self, channel, offset):
		if type(channel) != int:
			raise TypeError(channel)
		if (type(offset) != int) and (type(offset) != str):
			raise TypeError(offset)


		# offset is between -10 and +10 volt
		if (offset < -10) or (offset > 10):
			raise ValueError(offset)

		# note: althou the value-range for offset is able
		# to accomodate an offset between -10 and +10 Volt
		# the actual offset seams to be lmited to -2.5 to +2.5

		# round to nearest 0.01 value
		if offset > 0:
			offset=int(offset*100+0.5)+1000
		else:
			offset=int(offset*100-0.5)+1000

		cmd=self.__cmd2txt_ch(channel,jds6600.OFFSET1,jds6600.OFFSET2)

		self.__sendwritecmd(cmd,offset)
	# end set offset

	# set dutcycle
	def setdutycycle(self, channel, dutycycle):
		if type(channel) != int:
			raise TypeError(channel)
		if (type(dutycycle) != int) and (type(dutycycle) != str):
			raise TypeError(dutycycle)


		# dutycycle is between 0 and 100 %
		if (dutycycle < 0) or (dutycycle > 100):
			raise ValueError(dutycycle)

		# round to nearest 0.1 value
		dutycycle=int(dutycycle*10+0.5)

		cmd=self.__cmd2txt_ch(channel,jds6600.DUTYCYCLE1,jds6600.DUTYCYCLE2)

		self.__sendwritecmd(cmd,dutycycle)
	# end set dutycycle

	
	# set phase
	def setphase(self,phase):
		if (type(phase) != int) and (type(phase) != str):
			raise TypeError(phase)

		# hase is between -360 and 360
		if (phase < -360) or (phase > 360):
			raise ValueError(phase)

		if phase < 0:
			phase += 3600

		# round to nearest 0.1 value
		phase=int(phase*10+0.5)

		cmd=self.__cmd2txt(jds6600.PHASE)

		self.__sendwritecmd(cmd,phase)
	# end getphase

	
	#######################
	# Part 4: reading / changing mode
	# get mode
	def getmode(self):
		cmd=self.__cmd2txt(jds6600.MODE)

		self.__sendreadcmd(cmd)
		(mode,)=self.__getrespondsandparse(cmd)
		mode=int(mode)>>3

		# mode is in the list "modes". mode-name "" means undefinded
		try:
			(modeid,modetxt)=jds6600.modes[mode]
		except IndexError:
			raise UnexpectedValueError(mode)

		# modeid 3 is not valid and returns an id of -1
		if modeid >= 0:
			return modeid,modetxt
		# end if


		# modeif 4
		raise UnexpectedValueError(mode)

	# end getmode


	# set mode
	def setmode(self,mode, nostop=False):
		if (type(mode) == float):
			mode = int(mode)

		# type check 
		if (type(mode) != int) and (type(mode) != str):
			raise TypeError(mode)
		# end if



		modeid=-1
		# if mode is an integer, it should be between 0 and 9
		if type(mode) == int:
			if (mode < 0) or (mode > 9):
				raise ValueError(mode)
			# end if

			# modeid 3 / modetxt "" does not exist
			if mode == 3:
				raise ValueError("mode 3 does not exist")
			# end if

			
			# valid modeid
			modeid = mode

		else:
			# modeid 3 / modetxt "" does not exist
			if mode == "":
				raise ValueError("mode 3 does not exist")
			# end if

			# mode is string -> check list
			c=0 # counter
			
			for (mid,mtxt) in jds6600.modes:
				if mode.upper() == mtxt:
					# found it!!!
					modeid=mid
					break
				# end if
				c += 1
			else:
				# mode not found -> error
				raise ValueError(mode)
			# end for
		# end else - if

		# before changing mode, disable all actions (unless explicitally asked not to do)
		if nostop == False:
			self.__setaction("STOP")
		# endif

		# set mode
		cmd=self.__cmd2txt(jds6600.MODE)
		self.__sendwritecmd(cmd,modeid)
		
	# end setmode
	
	#######################
	# Part 5: functions common for all modes
	def stopallactions(self):
		# just send stop
		self.__setaction("STOP")
	# end stop all actions


	#######################
	# Part 6: "measure" mode

	# get coupling parameter (measure mode)
	def measure_getcoupling(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_COUP)

		self.__sendreadcmd(cmd)
		(coupling,)=self.__getrespondsandparse(cmd)
		coupling=int(coupling)

		try:
			return (coupling,jds6600.measure_coupling[coupling])
		except IndexError:
			raise UnexpectedValueError(coupling)
		# end try
	# end get coupling (measure mode)

	# get gate time (measure mode)
	#  get (measure mode)
	def measure_getgate(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_GATE)

		self.__sendreadcmd(cmd)
		(gate,)=self.__getrespondsandparse(cmd)
		gate=int(gate)

		# gate unit is 0.01 seconds
		gate /= 100

		return gate
	# end get gate (measure mode)


	# get Measure mode (freq or period)
	def measure_getmode(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_MODE)

		self.__sendreadcmd(cmd)
		(mode,)=self.__getrespondsandparse(cmd)
		mode=int(mode)

		try:
			return (mode,jds6600.measure_mode[mode])
		except IndexError:
			raise UnexpectedValueError(mode)
		# end try
	# end get mode (measure)


	
	# set measure coupling
	def measure_setcoupling(self,coupling):
		# type checks
		if type(coupling) == float: coupling = int(coupling) 
		if (type(coupling) != int) and (type(coupling) != str): raise TypeError(coupling)


		if type(coupling) == int:
			# coupling is 0 (DC) or 1 (AC)
			if (coupling != 0) and (coupling != 1):
				raise ValueError(coupling)

			coupl=coupling

		else:
			# string based
			
			coupling=coupling.upper()
			# spme shortcuts:
			if coupling == "AC": coupling = "AC(EXT.IN)"
			if coupling == "DC": coupling = "DC(EXT.IN)"

			c=0 # counter
			for mc in jds6600.measure_coupling:
				if coupling == mc:
					# found it
					coupl = c
					break
				c += 1
			else:
				errmsg="Unknown measure coupling: "+coupling
				raise ValueError(errmsg)
			# end else - for
		 # end else ) if (type is int or str?)

		# set mode
		cmd=self.__cmd2txt(jds6600.MEASURE_COUP)
		self.__sendwritecmd(cmd,coupl)

	# end set measure_coupling 

	# get gate time (measure mode)
	#  get (measure mode)
	def measure_setgate(self, gate):
		# check type
		if (type(gate) != int) and (type(gate) != float): raise TypeError(gate)

		# gate unit is 0.01 and is between 0 and 10
		if (gate <= 0) or (gate > 1000):
			raise ValueError(gate)

		gate = int(gate*100+0.5)

		# minimum is 0.01 second
		if gate == 0:
			gate = 1

		# set gate
		cmd=self.__cmd2txt(jds6600.MEASURE_GATE)
		self.__sendwritecmd(cmd,gate)
	# end get gate (measure mode)


	# set measure mode
	def measure_setmode(self,mode):
		# type checks
		if type(mode) == float: mode = int(mode) 
		if (type(mode) != int) and (type(mode) != str): raise TypeError(mode)


		if type(mode) == int:
			# mode is 0 (M.FREQ) or 1 (M.PRERIOD)
			if (mode != 0) and (mode != 1):
				raise ValueError(mode)

		else:
			# string based

			# make uppercase
			mode=mode.upper()
			
			# spme shortcuts:
			if mode== "FREQ": mode = "M.FREQ"
			if mode== "PERIOD": mode = "M.PERIOD"

			c=0 # counter
			for mm in jds6600.measure_mode:
				if mode == mm:
					# found it
					mode = c
					break
				c += 1
			else:
				errmsg="Unknown measure mode: "+mode
				raise ValueError(errmsg)
			# end else - for
		 # end else ) if (type is int or str?)

		# set mode
		cmd=self.__cmd2txt(jds6600.MEASURE_MODE)
		self.__sendwritecmd(cmd,mode)

	# end set measure_coupling 

	# get Measure freq. (lowres / Freq-mode)
	def measure_getfreq_f(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_FREQ_LOWRES)

		self.__sendreadcmd(cmd)
		(freq,)=self.__getrespondsandparse(cmd)

		# unit is 0.1 Hz
		return int(freq)/10
	# end get freq-Lowres (measure)

	# get Measure freq. (highes / Periode-mode)
	def measure_getfreq_p(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_FREQ_HIGHRES)

		self.__sendreadcmd(cmd)
		(freq,)=self.__getrespondsandparse(cmd)

		# unit is 0.001 Hz
		return int(freq)/1000
	# end get freq-Lowres (measure)

	# get Measure pulsewith +
	def measure_getpw1(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_PW1)

		self.__sendreadcmd(cmd)
		(period,)=self.__getrespondsandparse(cmd)

		# unit is 0.01 microsecond
		return int(period)/100
	# end get pulsewidth -

	# get Measure pulsewidth -
	def measure_getpw0(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_PW0)

		self.__sendreadcmd(cmd)
		(period,)=self.__getrespondsandparse(cmd)

		# unit is 0.01 microsecond
		return int(period)/100
	# end get pulsewidth +

	# get Measure total period
	def measure_getperiod(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_PERIOD)

		self.__sendreadcmd(cmd)
		(period,)=self.__getrespondsandparse(cmd)

		# unit is 0.01 microsecond
		return int(period)/100
	# end get total period

	# get Measure dutycycle
	def measure_getdutycycle(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_DUTYCYCLE)

		self.__sendreadcmd(cmd)
		(dutycycle,)=self.__getrespondsandparse(cmd)

		# unit is 0.1 %
		return int(dutycycle)/10
	# end get freq-Lowres (measure)

	# get Measure unknown value 1 (related to freq, inverse-related to gatetime)
	def measure_getu1(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_U1)

		self.__sendreadcmd(cmd)
		(u1,)=self.__getrespondsandparse(cmd)

		# unit is unknown, just return it
		return int(u1)
	# end get freq-Lowres (measure)

	# get Measure unknown value 2 (inverse related to freq)
	def measure_getu2(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_U2)

		self.__sendreadcmd(cmd)
		(u2,)=self.__getrespondsandparse(cmd)

		# unit is unknown, just return it
		return int(u2)
	# end get freq-Lowres (measure)

	# get Measure unknown value 3 (nverse related to freq)
	def measure_getu3(self):
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_U3)

		self.__sendreadcmd(cmd)
		(u3,)=self.__getrespondsandparse(cmd)

		# unit is unknown, just return it
		return int(u3)
	# end get freq-Lowres (measure)


	# get Measure all (all usefull data: freq_f, freq_p, pw1, pw0, period, dutycycle
	def measure_getall(self):

		# start with freq_q
		cmd=self.__cmd2txt(jds6600.MEASURE_DATA_FREQ_LOWRES)

		# do query for 6 values
		self.__sendreadcmd_n(cmd,6)
		(freq_f, freq_p, pw1, pw0, period, dutycycle)=self.__getrespondsandparse_n(cmd,6)

		# return all
		return (int(freq_f) / 10, int(freq_p) / 1000, int(pw1)/100, int(pw0)/100, int(period)/100, int(dutycycle)/10)
	# end get freq-Lowres (measure)



	#######################
	# Part 7: "Counter" mode

	# counter getcoupling is the same as measure getcoupling
	def counter_getcoupling(self):
		return self.measure_getcoupling()
	# end counter get coupling


	# counter setcoupling is the same as measure setcoupling
	def counter_setcoupling(self,coupling):
		self.measure_setcoupling(coupling)
	# end counter get coupling


	# counter - reset counter
	def counter_reset(self):
		# write 0 to register "COUNTER_RESETCOUNTER"
			cmd=self.__cmd2txt(jds6600.COUNTER_RESETCOUNTER)
			self.__sendwritecmd(cmd,0)
	# end counter reset counter

	# start counter mode
	def counter_start(self):
		mode=self.getmode()

		if mode[1] != "COUNTER":
			raise WrongMode()
		# end if

		# action start BURST mode
		self.__setaction("COUNT")
	# end burst_start
		

	def counter_stop(self):
		# just send stop
		self.__setaction("STOP")
	# end burst_start
		

	# get counter - counter
	def counter_getcounter(self):
		cmd=self.__cmd2txt(jds6600.COUNTER_DATA_COUNTER)

		self.__sendreadcmd(cmd)
		(counter,)=self.__getrespondsandparse(cmd)

		# unit is  1, just return data
		return int(counter)
	# end get counter - counter



	#######################
	# Part 8: "Sweep" mode

	# note, there are two "setmode" commands to enter "sweep" mode: "sweep_ch1' (mode 6) and "sweep_ch2" (mode 7)

	def sweep_getstartfreq(self):
		cmd=self.__cmd2txt(jds6600.SWEEP_STARTFREQ)

		self.__sendreadcmd(cmd)
		(freq,)=self.__getrespondsandparse(cmd)

		# unit is  1, just return data
		return int(freq)/100
	# end get sweep - startfreq

	def sweep_getendfreq(self):
		cmd=self.__cmd2txt(jds6600.SWEEP_ENDFREQ)

		self.__sendreadcmd(cmd)
		(freq,)=self.__getrespondsandparse(cmd)

		# unit is  1, just return data
		return int(freq)/100
	# end get sweep - startfreq

	def sweep_gettime(self):
		cmd=self.__cmd2txt(jds6600.SWEEP_TIME)

		self.__sendreadcmd(cmd)
		(time,)=self.__getrespondsandparse(cmd)

		# unit is  1, just return data
		return int(time)/10
	# end get sweep - startfreq


	# get sweep direction
	def sweep_getdirection(self):
		cmd=self.__cmd2txt(jds6600.SWEEP_DIRECTION)

		self.__sendreadcmd(cmd)
		(direction,)=self.__getrespondsandparse(cmd)
		direction=int(direction)

		try:
			return (direction,jds6600.sweep_direction[direction])
		except IndexError:
			raise UnexpectedValueError(direction)
		# end try
	# end get direction (sweep)

	# get sweep mode
	def sweep_getmode(self):
		cmd=self.__cmd2txt(jds6600.SWEEP_MODE)

		self.__sendreadcmd(cmd)
		(mode,)=self.__getrespondsandparse(cmd)
		mode=int(mode)

		try:
			return (mode,jds6600.sweep_mode[mode])
		except IndexError:
			raise UnexpectedValueError(mode)
		# end try
	# end get mode (measure)

	def sweep_setstartfreq(self, frequency):
		if (type(frequency) != int) and (type(frequency) != float): raise TypeError(frequency)

		# frequency should be between 0 and 60 MHz
		if (frequency < 0) or (frequency > 60000000):
			raise ValueError(frequency)

		# frequency unit is 0.01 Hz
		freq=int(frequency*100+0.5)

		cmd=self.__cmd2txt(jds6600.SWEEP_STARTFREQ)
		self.__sendwritecmd(cmd,freq)
	# end set start freq

	def sweep_setendfreq(self, frequency):
		if (type(frequency) != int) and (type(frequency) != float): raise TypeError(frequency)

		# frequency should be between 0 and 60 MHz
		if (frequency < 0) or (frequency > 60000000):
			raise ValueError(frequency)

		# frequency unit is 0.01 Hz
		freq=int(frequency*100+0.5)

		cmd=self.__cmd2txt(jds6600.SWEEP_ENDFREQ)
		self.__sendwritecmd(cmd,freq)
	# end set end freq


	def sweep_settime(self, time):
		if (type(time) != int) and (type(time) != float): raise TypeError(time)

		# time should be between 0 and 999.9 seconds
		if (time <= 0) or (time > 999.9):
			raise ValueError(time)

		# time unit is 0.1 second
		t=int(time*10+0.5)

		cmd=self.__cmd2txt(jds6600.SWEEP_TIME)
		self.__sendwritecmd(cmd,t)
	# end set end freq


	def sweep_setdirection(self, direction):
		if (type(direction) == float): direction = int(direction)
		if (type(direction) != int) and (type(direction) != str): raise TypeError(direction)

		if type(direction) == int:
			# mode is 0 (RISE°, 1 (FALL) or 2 (RISE&FALL)
			if (direction < 0) or (direction > 2):
				raise ValueError(direction)

		else:
			# string based

			# make uppercase
			direction=direction.upper()
			
			# spme shortcuts:
			if direction.upper() == "RISEFALL": direction = "RISE&FALL"
			if direction.upper() == "BOTH": direction = "RISE&FALL"

			c=0 # counter
			for sd in jds6600.sweep_direction:
				if direction == sd:
					# found it
					direction = c
					break
				c += 1
			else:
				errmsg="Unknown sweep direction: "+direction
				raise ValueError(errmsg)
			# end else - for
		 # end else ) if (type is int or str?)

		# set mode
		cmd=self.__cmd2txt(jds6600.SWEEP_DIRECTION)
		self.__sendwritecmd(cmd,direction)
	# end set direction (sweep)


	def sweep_setmode(self, mode):
		if (type(mode) == float): direction = int(mode)
		if (type(mode) != int) and (type(mode) != str): raise TypeError(mode)

		if type(mode) == int:
			# mode is 0 (LINEAR) or 1 (LOGARITHM)) 
			if (mode < 0) or (mode > 1):
				raise ValueError(mode)

		else:
			# string based

			# make uppercase
			mode=mode.upper()
			
			# spme shortcuts:
			if mode.upper() == "LIN": mode = "LINEAR"
			if mode.upper() == "LOG": mode = "LOGARITHM"

			c=0 # counter
			for sm in jds6600.sweep_mode:
				if mode == sm:
					# found it
					mode = c
					break
				c += 1
			else:
				errmsg="Unknown sweep mode: "+mode
				raise ValueError(errmsg)
			# end else - for
		 # end else ) if (type is int or str?)

		# set mode
		cmd=self.__cmd2txt(jds6600.SWEEP_MODE)
		self.__sendwritecmd(cmd,mode)
	# end set direction (sweep)




	# get sweep channel
	def sweep_getchannel(self):
		mode=self.getmode()

		if mode[1] == "SWEEP_CH1":
			return 1
		elif mode[1] == "SWEEP_CH2":
			return 2
		# end if - elif

		# not channel 1 or channel 2, return 0
		return 0
	# end sweep get_channel

	# set sweep channel
	def sweep_setchannel(self,channel):
		if type(channel) == float: channel=int(channel)
		if type(channel) != int: raise TypeError(channel)

		# new channel should be 1 or 2
		if (channel != 1) and (channel != 2):
			raise ValueError(channel)
		# end if

		# get current channel (1 or 2, or 0 if not in sweep mode)
		currentchannel=self.sweep_getchannel()

		# only swich if already in sweep mode
		if currentchannel == 0:
			raise WrongMode()
		#endif

		# switch if the new channel is different from current channel
		if channel != currentchannel:
			if channel == 1:
				self.setmode("SWEEP_CH1",nostop=True)
			else:
				self.setmode("SWEEP_CH2",nostop=True)
			# end else - if
		# end if
	# end sweep set channel
		

	# start sweep
	def sweep_start(self):
		mode=self.getmode()

		if (mode[1] != "SWEEP_CH1") and (mode[1] != "SWEEP_CH2"):
			raise WrongMode()
		# end if

		# action start BURST mode
		self.__setaction("SWEEP")
	# end sweep_start
		

	# stop sweep
	def sweep_stop(self):
		# just send stop
		self.__setaction("STOP")
	# end sweep_start
		


	##################################

	
	#######################
	# Part 9: PULSE

	def pulse_start(self):
		mode=self.getmode()

		if mode[1] != "PULSE"
			raise WrongMode()
		# end if

		# action start BURST mode
		self.__setaction("PULSE")
	# end burst_start
		

	def pulse_stop(self):
		# just send stop
		self.__setaction("STOP")
	# end burst_start


	#######################
	# Part 10: BURST

	def burst_start(self):
		mode=self.getmode()

		if mode[1] != "BURST":
			raise WrongMode()
		# end if

		# action start BURST mode
		self.__setaction("BURST")
	# end burst_start
		

	def burst_stop(self):
		# just send stop
		self.__setaction("STOP")
	# end burst_start
		

	##################################

# end class jds6600
