import rostopic
import tbkpy._core as tbkpy
from tbk_api import TBKApi
import rospy
import rospy.core
import rospy.msg
from msg_translate import translate
import sensor_msgs.point_cloud2 as pc2
import numpy as np
import pickle
class EPInfo:
    def __init__(self, msg_name, msg_type):
        self.msg_name = msg_name
        self.msg_type = msg_type
    def ep_info(self):
        ep_info = tbkpy.EPInfo()
        ep_info.msg_name = self.msg_name
        ep_info.name = "default"
        ep_info.msg_type = self.msg_type
        return ep_info

class ROStransponder:
    def __init__(self):
        rospy.init_node("ROStransponder", anonymous=True)
        tbkpy.init("ROStransponder")
        self.tbkapi = TBKApi()
        self.tbk_subscribers = {}
        self.tbk_publishers = {}
        self.ros_subscribers = {}
        self.ros_publishers = {}
        self.timer = rospy.Timer(rospy.Duration(3), self.timer_callback)
        # self.allow_topics = ["/cloud_registered", "/Odometry"]
    def timer_callback(self, event):
        """
        定时器回调函数，用于定期执行 rospub2tbkpub 方法
        """
        self.rospub2tbkpub()

    def rospub2tbkpub(self):
        ros_topics = self.get_ros_topic()
        tbk_topics = self.get_tbk_topic()
        
        for topic_name, topic_info in ros_topics.items():
            # Skip certain topics
            if topic_name in ["/rosout", "/rosout_agg","/livox/lidar"]:
                continue
            
            try:
                # Dynamically import the message type
                msg_module = self.import_message_type(topic_info.msg_type)
                
                # Create subscriber with the specific message type
                if topic_name not in self.ros_subscribers:
                    subscriber = rospy.Subscriber(
                        topic_name, 
                        msg_module, 
                        callback=lambda msg, topic_info=topic_info: self.cbk(msg, topic_info)
                    )
                    self.ros_subscribers[topic_name] = subscriber
                
                # Create TBK publisher if it doesn't exist
                if topic_name not in self.tbk_publishers:
                    # if topic_name not in self.allow_topics:
                    ep_info = topic_info.ep_info()
                    publisher = tbkpy.Publisher(ep_info)
                    self.tbk_publishers[topic_name] = publisher
            
            except Exception as e:
                print(f"Error processing topic {topic_name}: {e}")

    def cbk(self, msg, sender_info):
        """
        Callback function to handle incoming ROS messages
        """
        
        try:
            msg_name = sender_info.msg_name
            msg_type = sender_info.msg_type
            if msg._type == "sensor_msgs/PointCloud2" :
                # 读取点云数据
                points = pc2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
                point_list = np.array(list(points), dtype=np.float32)
                xyz_points = point_list[:, :3]  # 提取 x, y, z 坐标

                # 分批发送点云数据，每组3000个点
                batch_size = 3000
                num_points = xyz_points.shape[0]
                for i in range(0, num_points, batch_size):
                    batch_points = xyz_points[i:i + batch_size]  # 获取当前批次的点
                    serialized_points = pickle.dumps(batch_points)  # 序列化点数据
                    self.tbk_publishers[msg_name].publish(serialized_points)  # 发布当前批次的数据

            if msg._type == "nav_msgs/Odometry":
                Odometry = {
                    "secs": msg.header.stamp.secs,
                    "nsecs": msg.header.stamp.nsecs,
                    "frame_id": msg.header.frame_id,
                    "seq": msg.header.seq,
                    "pose":{
                        "position":{
                            "x": msg.pose.pose.position.x,
                            "y": msg.pose.pose.position.y,
                            "z": msg.pose.pose.position.z
                        },
                        "orientation":{
                            "x": msg.pose.pose.orientation.x,
                            "y": msg.pose.pose.orientation.y,
                            "z": msg.pose.pose.orientation.z,
                            "w": msg.pose.pose.orientation.w
                        }
                    }
                }
                Odometry = pickle.dumps(Odometry)
                self.tbk_publishers[msg_name].publish(Odometry)

            
        except Exception as e:
            print(f"Error in callback for {msg_name}: {e}")

    def import_message_type(self, message_type):
        """
        Dynamically import ROS message type
        """
        try:
            # Split the message type into package and message name
            package, msg_name = message_type.split("/")

            # Dynamically import the message module
            module = __import__(f"{package}.msg", fromlist=[msg_name])
            return getattr(module, msg_name)
        except Exception as e:
            print(f"Error importing message type {message_type}: {e}")
            raise

    def get_ros_topic(self):
        ros_topics = rostopic.get_topic_list()[0]
        ros_publishers = {}

        for topic in ros_topics:
            topic_name = topic[0]
            topic_type = topic[1]
            
            # Skip system topics
            if topic_name in ["/rosout", "/rosout_agg"]:
                continue
            
            msg_data = EPInfo(topic_name, topic_type)
            ros_publishers[topic_name] = msg_data

        return ros_publishers

    def get_tbk_topic(self):
        tbk_topics = self.tbkapi.message_tree["pubs"]
        tbk_publishers = {}
        for topic_key, topic_value in tbk_topics.items():
            for uuid, info in topic_value.items():
                ep_info = info.ep_info
                msg_name = ep_info.msg_name
                msg_type = ep_info.msg_type
                msg_data = EPInfo(msg_name, msg_type)
                tbk_publishers[msg_name] = msg_data
        return tbk_publishers

def main():
    transponder = ROStransponder()
    rospy.spin()

if __name__ == "__main__":
    main()