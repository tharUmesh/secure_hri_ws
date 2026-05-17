import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random


GESTURES = [
    ('Wave',       0.85, 0.97),
    ('Point',      0.80, 0.94),
    ('Stop',       0.88, 0.99),
    ('Thumbs_Up',  0.82, 0.96),
    ('Cross_Arms', 0.78, 0.92),
    ('Beckon',     0.79, 0.91),
]


class GestureNode(Node):
    def __init__(self):
        super().__init__('gesture_node')
        self.publisher_ = self.create_publisher(String, '/hri/gesture', 10)
        self.timer = self.create_timer(2.0, self.publish_gesture)
        self.get_logger().info(
            'Gesture Node started — publishing to /hri/gesture every 2s'
        )

    def publish_gesture(self):
        label, lo, hi = random.choice(GESTURES)
        confidence = round(random.uniform(lo, hi), 2)

        payload = json.dumps({
            'source': 'GestureModel_v1',
            'label': label,
            'confidence': confidence,
        })

        msg = String()
        msg.data = payload
        self.publisher_.publish(msg)
        self.get_logger().info(f'[PUB] {payload}')


def main(args=None):
    rclpy.init(args=args)
    node = GestureNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()