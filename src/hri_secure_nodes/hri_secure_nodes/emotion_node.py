import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import random


EMOTIONS = [
    ('Happy',    0.88, 0.97),
    ('Neutral',  0.80, 0.95),
    ('Angry',    0.75, 0.92),
    ('Panicked', 0.85, 0.99),
    ('Confused', 0.78, 0.93),
    ('Sad',      0.76, 0.91),
]


class EmotionNode(Node):
    def __init__(self):
        super().__init__('emotion_node')
        self.publisher_ = self.create_publisher(String, '/hri/emotion', 10)
        self.timer = self.create_timer(2.0, self.publish_emotion)
        self.get_logger().info(
            'Emotion Node started — publishing to /hri/emotion every 2s'
        )

    def publish_emotion(self):
        label, lo, hi = random.choice(EMOTIONS)
        confidence = round(random.uniform(lo, hi), 2)

        payload = json.dumps({
            'source': 'EmotionModel_v1',
            'label': label,
            'confidence': confidence,
        })

        msg = String()
        msg.data = payload
        self.publisher_.publish(msg)
        self.get_logger().info(f'[PUB] {payload}')


def main(args=None):
    rclpy.init(args=args)
    node = EmotionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()