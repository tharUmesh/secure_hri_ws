import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random


CONTEXTS = [
    ('Hospital_Corridor',  'High'),
    ('Hospital_Reception', 'Medium'),
    ('Museum_Gallery',     'Low'),
    ('Retail_Aisle',       'Medium'),
    ('Hospital_Ward',      'Low'),
]


class ContextNode(Node):
    def __init__(self):
        super().__init__('context_node')
        self.publisher_ = self.create_publisher(String, '/hri/context', 10)
        self.timer = self.create_timer(2.0, self.publish_context)
        self.get_logger().info(
            'Context Node started — publishing to /hri/context every 2s'
        )

    def publish_context(self):
        environment, crowding = random.choice(CONTEXTS)

        payload = json.dumps({
            'source': 'ContextModel_v1',
            'environment': environment,
            'crowding': crowding,
        })

        msg = String()
        msg.data = payload
        self.publisher_.publish(msg)
        self.get_logger().info(f'[PUB] {payload}')


def main(args=None):
    rclpy.init(args=args)
    node = ContextNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()