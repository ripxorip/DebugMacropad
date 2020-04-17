import keyboard
import time
import glob
import sys
import serial
import json
import math


def serial_ports(filt):
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
    filt_ports = []
    for p in ports:
        if filt in p:
            filt_ports.append(p)

    for port in filt_ports:
        try:
            s = serial.Serial(port, timeout=1)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

class debug_macro_pad():
    def __init__(self):
        self.last_input = None
        # Fix these maps
        self.current_map = {
            'func_out': 'a',
            'step_in': 'F5',
            'step_over': 'F5',
            'reset': 'F5',
            'run': 'F5',
            'bp': 'F5',
            'right_enc_count': 'F5',
            'left_enc_count': 'F5',
        }

        self.enc_counts = {
            'right_enc_count' : 0,
            'left_enc_count': 0
        }

    def get_delta(self, inp):
        if self.last_input == None:
            self.last_input = inp
            return inp
        ret = {}
        for i in inp:
            if not inp[i] == self.last_input[i]:
                ret[i] = inp[i]
        return ret

    def map_inputs(self, inp):
        ret = {}
        ret['func_out'] = inp['0']
        ret['step_in'] = inp['1']
        ret['step_over'] = inp['2']
        ret['reset'] = inp['3']
        ret['run'] = inp['4']
        ret['bp'] = inp['10']
        ret['left_enc_one'] = inp['6']
        ret['left_enc_two'] = inp['7']
        ret['right_enc_one'] = inp['8']
        ret['right_enc_two'] = inp['9']
        ret['right_enc_count'] = inp['right_enc_count']
        ret['left_enc_count'] = inp['left_enc_count']
        return ret

    def handle_encoder_pin(self, key, value):
        if 'enc_count' in key:
            num_before = math.floor(self.enc_counts[key])
            diff = value - self.last_input[key]
            self.enc_counts[key] += diff/4.00
            fract = self.enc_counts[key] - math.floor(self.enc_counts[key])
            if fract == 0.00:
                keyboard.press_and_release(self.current_map[key])


    def handle_signal(self, key, value):
        if 'enc' in key:
            self.handle_encoder_pin(key, value)
            return

        # Handle normal keys
        if value == 0:
            keyboard.press(self.current_map[key])
        else:
            keyboard.release(self.current_map[key])

    def process_input(self, inp):
        inmap = self.map_inputs(inp)
        delta = self.get_delta(inmap)

        for d in delta:
            self.handle_signal(d, delta[d])
        self.last_input = inmap

    def validate_packet(self, packet):
        ret = False
        try:
            pp = json.loads(packet)
            if pp['magic'] == 1337:
                ret = True
        except json.decoder.JSONDecodeError as e:
            print('Got illegal packet: ' + packet)
        return ret

    def open_port(self):
        ret = None
        ports = serial_ports('tty.usbserial')
        for p in ports:
            lines = []
            s = serial.Serial(p, 115200, timeout=1.5)
            lines.append(s.readline().decode())
            lines.append(s.readline().decode())
            for l in lines:
                if self.validate_packet(l):
                    ret = s
            if ret is not None:
                break
            s.close()
        return ret

    def communicate(self):
        # Will not return as long as
        # we have a valid connection
        print('Found keyboard; listening')
        try:
            last_pp = None
            while True:
                inp = self.port.readline()
                if not self.validate_packet(inp):
                    break
                self.process_input(json.loads(inp))
        except serial.serialutil.SerialException:
            print('Serial port broken..')

    def run(self):
        while True:
            port = self.open_port()
            if port is not None:
                self.port = port
                self.communicate()
            # We got here because we could not find any port
            # or the communication stopped working
            print('Communication lost searching for keyboard..')
            time.sleep(1)


def main():
    dmc = debug_macro_pad()
    dmc.run()

if __name__ == "__main__":
    main()
