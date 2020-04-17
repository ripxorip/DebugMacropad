import keyboard
import time
import glob
import sys
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    """
    for port in ports:
        try:
            s = serial.Serial(port, timeout=1)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    """
    return ports

class debug_macro_pad():
    def __init__(self):
        pass

    def open_port(self):
        ret = False
        ports = serial_ports()
        return ret

    def communicate(self):
        # Will not return as long as
        # we have a valid connection
        pass

    def run(self):
        while True:
            if self.open_port():
                self.communicate()
            # We got here because we could not find any port
            # or the communication stopped working

            time.sleep(1)


def main():
    print(serial_ports())
    dmc = debug_macro_pad()
    dmc.run()

if __name__ == "__main__":
    main()
