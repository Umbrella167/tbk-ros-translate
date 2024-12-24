import tbkpy._core as tbkpy
import time
tbkpy.init("TEST")
ep_info = tbkpy.EPInfo()
ep_info.msg_name = "test"
pub = tbkpy.Publisher(ep_info)
while True:
    pub.publish("test")
    time.sleep(1)