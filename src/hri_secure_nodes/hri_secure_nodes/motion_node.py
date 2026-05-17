import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random


MOTIONS = [
    ('Approaching',  0.4, 1.2),
    ('Retreating',   0.3, 0.9),
    ('Stationary',   0.0, 0.1),
    ('Running',      1.8, 3.5),
    ('Wandering',    0.2, 0.7),
]


class MotionNode(Node):
    def __init__(self):
        super().__init__('motion_node')
        self.publisher_ = self.create_publisher(String, '/hri/motion', 10)
        self.timer = self.create_timer(2.0, self.publish_motion)
        self.get_logger().info(
            'Motion Node started — publishing to /hri/motion every 2s'
        )

    def publish_motion(self):
        label, lo, hi = random.choice(MOTIONS)
        speed = round(random.uniform(lo, hi), 2)

        payload = json.dumps({
            'source': 'MotionModel_v1',
            'label': label,
            'speed_ms': speed,
        })

        msg = String()
        msg.data = payload
        self.publisher_.publish(msg)
        self.get_logger().info(f'[PUB] {payload}')


def main(args=None):
    rclpy.init(args=args)
    node = MotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()