from tzcp.ros.sensor_pb2 import IMU
from tzcp.ros.std_pb2 import *
from tzcp.ros.geometry_pb2 import *
from tzcp.ros.sensor_pb2 import *
class MsgTranslate:
    def __init__(self) -> None:
        self.MSG_TRANSLATE_DICT = {
            "sensor_msgs/PointCloud2": self.PointCloud2Protobuf,
        }


    # SUPPORT_TYPE
    def transform(self,ros_msg):
        """
        Transform ROS message to TBK message
        """
        msg_type = ros_msg._type
        if msg_type not in self.MSG_TRANSLATE_DICT:
            raise ValueError(f"Unsupported message type: {msg_type}")
        return self.MSG_TRANSLATE_DICT[msg_type](ros_msg)
        


    def PointCloud2Protobuf(self,ros_msg):
        """
        Transform ROS PointCloud2 message to Protobuf message
        """
        protobuf_msg = PointCloud()
        protobuf_msg.header.stamp.secs = ros_msg.header.stamp.secs
        protobuf_msg.header.stamp.nsecs = ros_msg.header.stamp.nsecs
        protobuf_msg.header.frame_id = ros_msg.header.frame_id
        protobuf_msg.height = ros_msg.height
        protobuf_msg.width = ros_msg.width
        for field in ros_msg.fields:
            proto_field = PointField()
            proto_field.name = field.name
            proto_field.offset = field.offset
            proto_field.count = field.count

            # 映射 ROS 数据类型到 Protobuf 的 DataType
            if field.datatype == 1:  # INT8
                proto_field.datatype = PointField.DataType.INT8
            elif field.datatype == 2:  # UINT8
                proto_field.datatype = PointField.DataType.UINT8
            elif field.datatype == 3:  # INT16
                proto_field.datatype = PointField.DataType.INT16
            elif field.datatype == 4:  # UINT16
                proto_field.datatype = PointField.DataType.UINT16
            elif field.datatype == 5:  # INT32
                proto_field.datatype = PointField.DataType.INT32
            elif field.datatype == 6:  # UINT32
                proto_field.datatype = PointField.DataType.UINT32
            elif field.datatype == 7:  # FLOAT32
                proto_field.datatype = PointField.DataType.FLOAT32
            elif field.datatype == 8:  # FLOAT64
                proto_field.datatype = PointField.DataType.FLOAT64
            else:
                proto_field.datatype = PointField.DataType.DATA_TYPE_UNKNOWN  # 默认值

            protobuf_msg.fields.append(proto_field)
            protobuf_msg.is_bigendian = ros_msg.is_bigendian
            protobuf_msg.point_step = ros_msg.point_step
            protobuf_msg.row_step = ros_msg.row_step
            protobuf_msg.data = ros_msg.data  # 二进制点云数据
            protobuf_msg.is_dense = ros_msg.is_dense
            return protobuf_msg
translate = MsgTranslate()