#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Plot CSI(Linux 802.11n CSI Tool) in real time

Usage:
    1. python3 csirealtime.py
    2. python3 csiserver.py ../material/5300/dataset/sample_0x5_64_3000.dat 3000 500
"""

import socket
import threading

import csiread
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np

cache_len = 1000
cache_data1 = [np.nan] * cache_len
cache_data2 = [np.nan] * cache_len
cache_data3 = [np.nan] * cache_len
mutex = threading.Lock()


class GetDataThread(threading.Thread):
    def run(self):
        update_background()


def update_background():
    csidata = csiread.Intel(None, 3, 1)

    # config
    global cache_data1, cache_data2, cache_data3, mutex
    count = 0
    address_src = ('127.0.0.1', 10086)
    address_des = ('127.0.0.1', 10010)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(address_des)
        while True:
            data, address_src = s.recvfrom(4096)
            msg_len = len(data)

            code = csidata.pmsg(data)
            if code == 0xbb:
                scaled_csi_sm = csidata.get_scaled_csi()[0]
                mutex.acquire()
                cache_data1.pop(0)
                cache_data1.append(scaled_csi_sm[15, 0, 0])
                cache_data2.pop(0)
                cache_data2.append(scaled_csi_sm[15, 1, 0])
                cache_data3.pop(0)
                cache_data3.append(scaled_csi_sm[15, 2, 0])
                mutex.release()
                count += 1
            if count % 100 == 0:
                print('receive %d bytes [msgcnt=%u]' % (msg_len, count))


def realtime_plot():
    fig, ax = plt.subplots()
    plt.title('csi-amplitude')
    plt.xlabel('packets')
    plt.ylabel('amplitude')
    ax.set_ylim(0, 40)
    ax.set_xlim(0, cache_len)
    x = np.arange(0, cache_len, 1)

    line1,  = ax.plot(x, np.abs(cache_data1), linewidth=1.0, label='subcarrier_15_0_0')
    line2,  = ax.plot(x, np.abs(cache_data2), linewidth=1.0, label='subcarrier_15_1_0')
    line3,  = ax.plot(x, np.abs(cache_data3), linewidth=1.0, label='subcarrier_15_2_0')
    plt.legend()

    def init():
        line1.set_ydata([np.nan] * len(x))
        line2.set_ydata([np.nan] * len(x))
        line3.set_ydata([np.nan] * len(x))
        return line1, line2, line3,

    def animate(i):
        global cache_data1, cache_data2, cache_data3, mutex
        mutex.acquire()
        line1.set_ydata(np.abs(cache_data1))
        line2.set_ydata(np.abs(cache_data2))
        line3.set_ydata(np.abs(cache_data3))
        mutex.release()
        return line1, line2, line3,

    ani = animation.FuncAnimation(fig, animate, init_func=init, interval=1000/25, blit=True)
    plt.show()


if __name__ == '__main__':
    task = GetDataThread()
    task.start()
    realtime_plot()
