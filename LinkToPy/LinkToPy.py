from __future__ import print_function
import socket
import edn_format
import os
import numpy as np
import time
import threading
import errno
from socket import error as socket_error
import warnings

class LinkInterface():
    """A simple python client to communicate with carabiner (a Abelton Link connector)
        Carabiner server must be running to use. Requires edn_format [$pip install edn_format]"""

    def __init__(self, path_to_carabiner, tcp_ip='127.0.0.1', tcp_port=17000, buffer_size=1024, callbacks=None):
        self._tcp_ip = tcp_ip
        self._tcp_port = tcp_port
        self._buffer_size = buffer_size
        self.start_ = -1
        self.bpm_ = 120
        self.beat_ = -1

        if callbacks is None:
            self.callbacks = {}
        else:
            self.callbacks = callbacks

        self.start_carabiner_and_open_socket(path_to_carabiner)

        thread = threading.Thread(target=self._listener)
        thread.daemon = True
        thread.start()
        print('LinkInterface Started')

    def decode_edn_msg(self, msg):
        """Decodes a TCP message from Carabiner to python dictionary"""
        msg = msg.decode()
        msg_type = msg[:msg.index(' {')]
        striped_msg = msg[msg.index('{'):]
        decoded_msg = edn_format.loads(striped_msg)

        # Because the edn_format package does not return normal dam dicts (or string keywords). What dicts.
        if type(decoded_msg) is edn_format.immutable_dict.ImmutableDict:
            decoded_msg = {str(key).strip(':'): value for key, value in decoded_msg.dict.items()}

        return msg_type, decoded_msg

    def status(self, callback=None):
        """Wrapper for Status"""
        self.s.send(b'status')
        if callback is not None:
            self.callbacks['status'] = callback

    def set_bpm(self, bpm, callback=None):
        """Wrapper for bpm"""
        msg = 'bpm ' + str(bpm)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['bpm'] = callback

    def beat_at_time(self, time_in_ms, quantum=8, callback=None):
        """Wrapper for Beat At Time"""
        msg = 'beat-at-time ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['beat-at-time'] = callback

    def time_at_beat(self, beat, quantum=8, callback=None):
        """Wrapper for Time At Beat"""
        msg = 'time-at-beat ' + str(beat) + ' ' + str(quantum)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['time-at-beat'] = callback

    def phase_at_time(self, time_in_ms, quantum=8, callback=None):
        """Wrapper for Phase At Time"""
        msg = 'phase-at-time ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['phase-at-time'] = callback

    def force_beat_at_time(self, beat, time_in_ms, quantum=8, callback=None):
        """Wrapper for Beat At Time"""
        msg = 'force-beat-at-time ' + str(beat) + ' ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['force-beat-at-time'] = callback

    def request_beat_at_time(self, beat, time_in_ms, quantum=8, callback=None):
        msg = 'request-beat-at-time ' + str(beat) + ' ' + str(time_in_ms) + ' ' + str(quantum)
        self.s.send(msg.encode())
        if callback is not None:
            self.callbacks['request-beat-at-time'] = callback

    # def time_of_next_beat(self, quantum=8):
    #     """Returns a tuple (beat, time) that specifies the next whole beat number at its time,
    #     in ms (for the given quantum) - this needs work..."""
    #     ret = self.beat_at_time(self.now(), quantum)
    #     next_beat = np.ceil(ret['beat'])
    #     ret = self.time_at_beat(next_beat, quantum)
    #     return (ret['beat'], ret['when'])
    #
    # def test_timer(self):
    #     """A function to test the error in clock times as provided by link vs system time
    #     This should be run without anny peers connected - broken"""
    #     status = self.status()
    #     bpm = int(status['bpm'])
    #     beats_per_ms = bpm / 60.0 / 1000.0 / 1000.0
    #     ms_per_beat = 1.0 / beats_per_ms
    #     beat, time_of_beat = self.time_of_next_beat()
    #     # Next 100 beats:
    #     beat_times = np.array([time_of_beat + beat_inc * ms_per_beat for beat_inc in range(0, bpm)])
    #     beats = np.array([beat + beat_inc for beat_inc in range(0, bpm)])
    #     beat_diff = []
    #     print('Beginning bpm beat test, this will take 1 minute')
    #     for beat_idx, beat_time in enumerate(beat_times):
    #         while self.now() < beat_time:
    #             pass
    #         ret = self.beat_at_time(self.now())
    #         beat_diff.append(ret['beat'] - beats[beat_idx])
    #     print('Mean (std) of difference between system time and link time @ bpm =', bpm, 'is', np.mean(beat_diff),
    #           ' (' + str(np.std(beat_diff)) + ') beats')
    #     print('Note that is includes TCP and carabiner processing times, so a small positive number is ok :)')

    def now(self):
        """Returns the monotonic system time as used by Link. This is in ms, and is the same format as 'start'
        See the Carabiner note on Clocks for more information"""
        return int(time.monotonic() * 1000 * 1000)

    def start_carabiner(self, path_to_car):
        print(path_to_car)
        os.system(path_to_car +" >car_logs.log")

    def start_carabiner_and_open_socket(self, carabiner_path):
        thread = threading.Thread(target=self.start_carabiner, args=[carabiner_path])
        thread.start()
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        not_connected = True
        not_connected_ticker = 0
        while not_connected:
            try:
                self.s.connect((self._tcp_ip, self._tcp_port))
                not_connected = False
            except socket_error as serr:
                if serr.errno != errno.ECONNREFUSED:
                    # Not the error we are looking for, re-raise
                    raise serr
                not_connected_ticker += 1
                if not_connected_ticker > 30:
                    warnings.warn('Socket Connection Timeout, Carabiner could not be started')
                    break
                print('Waiting for Carabiner')
                time.sleep(0.1)

    def _listener(self):
        while True:
            msg = self.s.recv(self._buffer_size)
            msg_type, msg_data = self.decode_edn_msg(msg)

            if msg_type == 'status':
                self.bpm_ = msg_data['bpm']
                self.beat_ = msg_data['beat']
                self.start_ = msg_data['start']

            if msg_type == 'time_at_beat':
                self.next_beat_ = (msg_data['beat'], msg_data['when'])

            if msg_type in self.callbacks:
                self.callbacks[msg_type](msg_data)

    def __del__(self):
        self.s.close()

if __name__ == "__main__":
    link = LinkInterface("/mnt/c/Users/bdyet/GoogleDrive/PersonalProjects/carabiner/build/bin/Carabiner")

    while 1:
        link.status()
        time.sleep(0.1)
        print(link.bpm_)
    # print(link.status())
    # link.test_timer()
