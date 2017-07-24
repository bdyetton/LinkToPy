import socket
import edn_format
import numpy as np
import time

class LinkListener():
    """A simple python client to communicate with carabiner (a Abelton Link connector)
    Carabiner server must be running to use. Requires edn_format [$pip install edn_format]"""

    def __init__(self, tcp_ip='127.0.0.1', tcp_port=17000, buffer_size=1024):
        self.tcp_ip = tcp_ip
        self.tcp_port = tcp_port
        self.buffer_size = buffer_size
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((tcp_ip, tcp_port))
        self.start = -1
        self.bpm = 120

    def decode_edn_msg(self, msg):
        """Decodes a TCP message from Carabiner to python dictionary"""
        msg = msg.decode()
        striped_msg = msg[msg.index('{'):]
        decoded_msg = edn_format.loads(striped_msg)

        # Because the edn_format package does not return normal dam dicts (or string keywords). What dicts.
        if type(decoded_msg) is edn_format.immutable_dict.ImmutableDict:
            decoded_msg = {str(key).strip(':'): value for key, value in decoded_msg.dict.items()}

        return decoded_msg

    def status(self):
        """Wrapper for Status"""
        self.s.send(b'status')
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def set_bpm(self, bpm):
        """Wrapper for bpm"""
        msg = 'bpm ' + str(bpm)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def beat_at_time(self, time_in_ms, quantum=8):
        """Wrapper for Beat At Time"""
        msg = 'beat-at-time ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def time_at_beat(self, beat, quantum=8):
        """Wrapper for Time At Beat"""
        msg = 'time-at-beat ' + str(beat) + ' ' + str(quantum)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def phase_at_time(self, time_in_ms, quantum=8):
        """Wrapper for Phase At Time"""
        msg = 'phase-at-time ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def force_beat_at_time(self, beat, time_in_ms, quantum=8):
        """Wrapper for Beat At Time"""
        msg = 'force-beat-at-time ' + str(beat) + ' ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def request_beat_at_time(self, beat, time_in_ms, quantum=8):
        msg = 'request-beat-at-time ' + str(beat) + ' ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        return_msg = self.s.recv(self.buffer_size)
        return self.decode_edn_msg(return_msg)

    def time_of_next_beat(self, quantum=8):
        """Returns a tuple (beat, time) that specifies the next whole beat number at its time,
        in ms (for the given quantum)"""
        ret = self.beat_at_time(self.now(), quantum)
        next_beat = np.ceil(ret['beat'])
        ret = self.time_at_beat(next_beat, quantum)
        return (ret['beat'], ret['when'])

    def __del__(self):
        self.s.close()

    def test_timer(self):
        """A function to test the error in clock times as provided by link vs system time"""
        status = self.status()
        bpm = int(status['bpm'])
        start = status['bpm']
        beats_per_ms = bpm / 60.0 / 1000.0 / 1000.0
        ms_per_beat = 1.0 / beats_per_ms
        beat, time_of_beat = self.time_of_next_beat()
        #Next 100 beats:
        beat_times = np.array([time_of_beat+beat_inc*ms_per_beat for beat_inc in range(0, bpm)])
        beats = np.array([beat+beat_inc for beat_inc in range(0, bpm)])
        beat_diff = []
        print('Beginning bpm beat test, this will take 1 minute')
        for beat, beat_time in zip(beats, beat_times):
            while self.now() < beat_time:
                pass
            ret = self.beat_at_time(self.now())
            beat_diff.append(ret['beat'] - beat)
        print('Mean (std) of difference between system time and link time @ bpm =',bpm, 'is', np.mean(beat_diff), ' ('+str(np.std(beat_diff))+') beats')
        print('Note that is includes TCP and carabiner processing times, so a small positive number is ok :)')

    def now(self):
        """Returns the monotonic system time as used by Link. This is in ms, and is the same format as 'start'
        See the Carabiner note on Clocks for more information"""
        return int(time.monotonic() * 1000 * 1000)


if __name__ == "__main__":
    link = LinkListener()
    print(link.status())

    link.test_timer()
