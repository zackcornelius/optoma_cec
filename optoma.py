import serial


class Optoma:

    port = None
    serial = None
    proj_id = 1

    def _open_serial(self):
        if self.serial and self.serial.is_open:
            return
        if self.port is not None:
            self.serial = serial.Serial(self.port, 9600, timeout=0.25)

    def __init__(self, port, proj_id=0):
        self.port = port
        self.proj_id = proj_id
        self._open_serial()

    def _send_command(self, command, argument=None, response_length=1):
        if argument is None:
            argument = ""
        else:
            argument = " %s" % argument
        self.serial.reset_input_buffer()
        self.serial.write(('~%02d%s%s\x0d' % (self.proj_id, command, argument)).encode('utf-8'))
        self.serial.flush()
        return self.serial.read(response_length).decode()


    def turn_on(self):
        self._send_command('00', '1')

    def turn_off(self):
        self._send_command('00', '0')

    def volume_up(self):
        self._send_command('140', '9')

    def volume_down(self):
        self._send_command('140', '10')

    def software_version(self):
        return self._send_command('122', '1', 12)

    def status(self):
        sources = {
            0: "None",
            1: "HDMI 1",
            2: "HDMI 2",
            3: "VGA",
            4: "S-Video",
            5: "Video",
            }
        status = {}
        st = self._send_command('150', '1', response_length=15)
        if st == 'F':
            print("Status request failed")
            return None
        if st[0:2] != "OK":
            print(st)
            print(st[0:2])
            print("Requeseted status, but didn't get OK back")
            return None
        status["power"] = int(st[2]) == 1
        status["lamp_hours"] = int(st[3:8])
        status["source"] = int(st[8:10])
        status["source_name"] = sources.get(status["source"], "Unknown")
        status["fw"] = str(st[10:14])
        status["mode"] = int(st[14:16])

        print(st)
        return status
    
    def power_status(self):
        st = self._send_command('124', '1', 4)
        if st[0:2] != "OK":
            print("Requested power status, but didn't get OK back")
            return False
        return int(st[2]) == 1
