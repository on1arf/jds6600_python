import click

from jds6600 import jds6600 as JDS6600

USB_PATH = '/dev/ttyUSB0'

class JDS6600_Cli:
    def __init__(self):
        self.jds6600 = JDS6600(USB_PATH)

@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = JDS6600_Cli()


#########################
# Part 0: API information
@click.group("api", help="Get API information")
@click.pass_obj
def api_group(cli: JDS6600_Cli):
    pass

@api_group.command(help="Get the API version")
@click.pass_obj
def getAPIinfo_version(cli: JDS6600_Cli):
    print(cli.jds6600.getAPIinfo_version())

@api_group.command(help="Get the API release number")
@click.pass_obj
def getAPIinfo_release(cli: JDS6600_Cli):
    print(cli.jds6600.getAPIinfo_release())


#############################
# Part 1: information queries
@click.group("information", help="Get meta information")
@click.pass_obj
def info_group(cli: JDS6600_Cli):
    pass

@info_group.command(help="Get waveformlist")
@click.pass_obj
def getinfo_waveformlist(cli: JDS6600_Cli):
    print(cli.jds6600.getinfo_waveformlist())

@info_group.command(help="Get modelist")
@click.pass_obj
def getinfo_modelist(cli: JDS6600_Cli):
    print(cli.jds6600.getinfo_modelist())


##################################
# Part 2: reading basic parameters
@click.group("read", help="Read parameters")
@click.pass_obj
def read_group(cli: JDS6600_Cli):
    pass

@read_group.command(help="Get devicetype")
@click.pass_obj
def getinfo_devicetype(cli: JDS6600_Cli):
    print(cli.jds6600.getinfo_devicetype())

@read_group.command(help="Get device serialnumber")
@click.pass_obj
def getinfo_serialnumber(cli: JDS6600_Cli):
    print(cli.jds6600.getinfo_serialnumber())

@read_group.command(help="Get channelenable")
@click.pass_obj
def getchannelenable(cli: JDS6600_Cli):
    print(cli.jds6600.getchannelenable())

@read_group.command(help="Get waveform")
@click.argument("channel", type=int)
@click.pass_obj
def getwaveform(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getwaveform(channel))

@read_group.command(help="Get frequency_m")
@click.argument("channel", type=int)
@click.pass_obj
def getfrequency_m(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getfrequency_m(channel))

@read_group.command(help="Get frequency")
@click.argument("channel", type=int)
@click.pass_obj
def getfrequency(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getfrequency(channel))

@read_group.command(help="Get amplitude")
@click.argument("channel", type=int)
@click.pass_obj
def getamplitude(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getamplitude(channel))

@read_group.command(help="Get offset")
@click.argument("channel", type=int)
@click.pass_obj
def getoffset(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getoffset(channel))

@read_group.command(help="Get dutycycle")
@click.argument("channel", type=int)
@click.pass_obj
def getdutycycle(cli: JDS6600_Cli, channel: int):
    print(cli.jds6600.getdutycycle(channel))

@read_group.command(help="Get phase")
@click.pass_obj
def getphase(cli: JDS6600_Cli):
    print(cli.jds6600.getphase())


##################################
# Part 3: writing basic parameters
@click.group("write", help="Write  parameters")
@click.pass_obj
def write_group(cli: JDS6600_Cli):
    pass

@write_group.command(help="Set channelenable")
@click.argument("channel1", type=bool)
@click.argument("channel2", type=bool)
@click.pass_obj
def setchannelenable(cli: JDS6600_Cli, channel1, channel2):
    cli.jds6600.setchannelenable(channel1, channel2)
    print("Done")

@write_group.command(help="Set waveform")
@click.argument("channel", type=int)
@click.argument("waveform", type=int)
@click.pass_obj
def setwaveform(cli: JDS6600_Cli, channel, waveform):
    cli.jds6600.setwaveform(channel, waveform)
    print("Done")

@write_group.command(help="Set frequency")
@click.argument("channel", type=int)
@click.argument("frequency", type=float)
@click.pass_obj
def setfrequency(cli: JDS6600_Cli, channel, frequency):
    cli.jds6600.setfrequency(channel, frequency)
    print("Done")

@write_group.command(help="Set amplitude")
@click.argument("channel", type=int)
@click.argument("amplitude", type=float)
@click.pass_obj
def setamplitude(cli: JDS6600_Cli, channel, amplitude):
    cli.jds6600.setamplitude(channel, amplitude)
    print("Done")

@write_group.command(help="Set offset")
@click.argument("channel", type=int)
@click.argument("offset", type=float)
@click.pass_obj
def setoffset(cli: JDS6600_Cli, channel, offset):
    cli.jds6600.setoffset(channel, offset)
    print("Done")

@write_group.command(help="Set dutycycle")
@click.argument("channel", type=int)
@click.argument("dutycycle", type=float)
@click.pass_obj
def setdutycycle(cli: JDS6600_Cli, channel, dutycycle):
    cli.jds6600.setdutycycle(channel, dutycycle)
    print("Done")

@write_group.command(help="Set phase")
@click.argument("phase", type=float)
@click.pass_obj
def setphase(cli: JDS6600_Cli, phase):
    if phase < 0:
        phase = 0
    elif phase > 360:
        phase = 360
    cli.jds6600.setphase(phase)
    print("Done")


#################################
# Part 4: reading / changing mode
@click.group("mode", help="Read / change mode")
@click.pass_obj
def mode_group(cli: JDS6600_Cli):
    pass

@mode_group.command(help="Get Mode")
@click.pass_obj
def getmode(cli: JDS6600_Cli):
    print(cli.jds6600.getmode())

@mode_group.command(help="Set Mode")
@click.argument("mode", type=int)
@click.pass_obj
def setmode(cli: JDS6600_Cli, mode):
    cli.jds6600.setmode(mode)
    print("Done")

########################################
# Part 5: functions common for all modes
@click.group("common", help="Common functions for all modes")
@click.pass_obj
def common_group(cli: JDS6600_Cli):
    pass

@common_group.command(help="Stop all actions")
@click.pass_obj
def stop(cli: JDS6600_Cli):
    cli.jds6600.stopallactions()

########################
# Part 6: "measure" mode
@click.group("measure", help="Measure mode functions")
@click.pass_obj
def measure_group(cli: JDS6600_Cli):
    pass

@measure_group.command(help="Measure get coupling")
@click.pass_obj
def measure_getcoupling(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getcoupling())

@measure_group.command(help="Measure get gate")
@click.pass_obj
def measure_getgate(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getgate())

@measure_group.command(help="Measure get mode")
@click.pass_obj
def measure_getmode(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getmode())

@measure_group.command(help="Measure get coupling")
@click.argument("coupling", type=int)
@click.pass_obj
def measure_setcoupling(cli: JDS6600_Cli, coupling):
    cli.jds6600.measure_setcoupling(coupling)
    print("Done")

@measure_group.command(help="Measure get gate")
@click.argument("gate", type=float)
@click.pass_obj
def measure_setgate(cli: JDS6600_Cli, gate):
    cli.jds6600.measure_setgate(gate)
    print("Done")

@measure_group.command(help="Measure get mode")
@click.argument("mode", type=int)
@click.pass_obj
def measure_setmode(cli: JDS6600_Cli, mode):
    cli.jds6600.measure_setmode(mode)
    print("Done")

@measure_group.command(help="Measure get freq_f")
@click.pass_obj
def measure_getfreq_f(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getfreq_f())

@measure_group.command(help="Measure get freq_p")
@click.pass_obj
def measure_getfreq_p(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getfreq_p())

@measure_group.command(help="Measure get pw1")
@click.pass_obj
def measure_getpw1(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getpw1())

@measure_group.command(help="Measure get pw0")
@click.pass_obj
def measure_getpw0(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getpw0())

@measure_group.command(help="Measure get period")
@click.pass_obj
def measure_getperiod(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getperiod())

@measure_group.command(help="Measure get dutycycle")
@click.pass_obj
def measure_getdutycycle(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getdutycycle())

@measure_group.command(help="Measure get u1")
@click.pass_obj
def measure_getu1(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getu1())

@measure_group.command(help="Measure get u2")
@click.pass_obj
def measure_getu2(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getu2())

@measure_group.command(help="Measure get u3")
@click.pass_obj
def measure_getu3(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getu3())

@measure_group.command(help="Measure get all")
@click.pass_obj
def measure_getall(cli: JDS6600_Cli):
    print(cli.jds6600.measure_getall())


########################
# Part 7: "Counter" mode
@click.group("counter", help="Counter mode functions")
@click.pass_obj
def counter_group(cli: JDS6600_Cli):
    pass

@counter_group.command(help="Counter get coupling")
@click.pass_obj
def counter_getcoupling(cli: JDS6600_Cli):
    print(cli.jds6600.counter_getcoupling())

@counter_group.command(help="Counter get counter")
@click.pass_obj
def counter_getcounter(cli: JDS6600_Cli):
    print(cli.jds6600.counter_getcounter())

@counter_group.command(help="Counter set coupling")
@click.argument("coupling", type=int)
@click.pass_obj
def counter_setcoupling(cli: JDS6600_Cli, coupling):
    cli.jds6600.counter_setcoupling(coupling)
    print("Done")

@counter_group.command(help="Counter reset")
@click.pass_obj
def counter_reset(cli: JDS6600_Cli, mode):
    cli.jds6600.counter_reset()
    print("Done")

@counter_group.command(help="Counter start")
@click.pass_obj
def counter_start(cli: JDS6600_Cli, mode):
    cli.jds6600.counter_start()
    print("Done")

@counter_group.command(help="Counter stop")
@click.pass_obj
def counter_stop(cli: JDS6600_Cli, mode):
    cli.jds6600.counter_stop()
    print("Done")


# Add all subgroups to the main group
cli.add_command(api_group)
cli.add_command(info_group)
cli.add_command(read_group)
cli.add_command(write_group)
cli.add_command(mode_group)
cli.add_command(common_group)
cli.add_command(measure_group)
cli.add_command(counter_group)


if __name__ == '__main__':
    cli()
