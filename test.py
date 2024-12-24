from tbkpy.socket.udp import UDPMultiCastReceiver, UDPReceiver
import numpy as np
import struct


def f(msg):
    print(msg)


# point_data_port_ = UDPReceiver(port=56301, callback=f)
point_data_port_ = UDPReceiver(port=56301, bind_ip="192.168.31.212", callback=f)

while True:
    pass
