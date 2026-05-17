import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json


class RogueNode(Node):
    """Simulates a network attacker attempting to inject a false
    EMERGENCY signal into the Fusion Engine's emotion topic.

    In the unsecured demo  → this message reaches the Fusion Engine.
    In the secured demo    → SROS2 rejects this node (no valid cert).
    """

    def __init__(self):
        super().__init__('rogue_node')
        self.publisher_ = self.create_publisher(String, '/hri/emotion', 10)
        self.timer = self.create_timer(1.5, self._inject)

        self.get_logger().warn('━' * 50)
        self.get_logger().warn('  ROGUE NODE ACTIVE')
        self.get_logger().warn('  Injecting fake PANICKED signals into /hri/emotion')
        self.get_logger().warn('━' * 50)

    def _inject(self):
        payload = json.dumps({
            'source': '*** ATTACKER ***',
            'label':  'Panicked',
            'confidence': 1.0,
            'note': 'INJECTED — THIS IS A FAKE EMERGENCY',
        })

        msg = String()
        msg.data = payload
        self.publisher_.publish(msg)
        self.get_logger().warn(f'[ATTACK PAYLOAD SENT] {payload}')


def main(args=None):
    rclpy.init(args=args)
    node = RogueNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()