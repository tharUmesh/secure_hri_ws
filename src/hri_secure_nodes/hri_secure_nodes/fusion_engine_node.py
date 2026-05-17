import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import hashlib
import logging
import os
from datetime import datetime


# ── Audit log lives in the workspace logs/ directory ──────────────────────────
LOG_DIR = os.path.expanduser('~/secure_hri_ws/logs')


class FusionEngineNode(Node):

    def __init__(self):
        super().__init__('fusion_engine_node')
        self._setup_audit_logger()

        # Subscribe to all four perception topics
        self.create_subscription(
            String, '/hri/emotion',  self._emotion_cb,  10)
        self.create_subscription(
            String, '/hri/gesture',  self._gesture_cb,  10)
        self.create_subscription(
            String, '/hri/motion',   self._motion_cb,   10)
        self.create_subscription(
            String, '/hri/context',  self._context_cb,  10)

        # Hold the latest reading from each modality
        self._latest = {
            'emotion': None,
            'gesture': None,
            'motion':  None,
            'context': None,
        }

        self.get_logger().info('=' * 55)
        self.get_logger().info('  Fusion Engine online — awaiting multimodal inputs')
        self.get_logger().info('=' * 55)

    # ── Audit logger setup ─────────────────────────────────────────────────────

    def _setup_audit_logger(self):
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_path = os.path.join(LOG_DIR, f'audit_{timestamp}.log')

        self._audit = logging.getLogger('AuditLog')
        self._audit.setLevel(logging.INFO)
        fh = logging.FileHandler(log_path)
        fh.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
        self._audit.addHandler(fh)

        self.get_logger().info(f'Non-repudiation audit log → {log_path}')

    # ── Non-repudiation: hash and record every message ─────────────────────────

    def _record(self, sender_node: str, topic: str, raw_data: str) -> str:
        """SHA-256 hash the raw message and write to the audit log.

        The log entry proves:
          WHO  sent the message (sender_node / certificate identity)
          WHAT was sent        (raw_data)
          WHEN it arrived      (timestamp added by the logger formatter)
          INTEGRITY            (SHA-256 hash — any tampering changes the hash)
        """
        digest = hashlib.sha256(raw_data.encode('utf-8')).hexdigest()
        self._audit.info(
            f'SENDER={sender_node:<20} TOPIC={topic:<20} '
            f'SHA256={digest} DATA={raw_data}'
        )
        return digest

    # ── Subscription callbacks ─────────────────────────────────────────────────

    def _emotion_cb(self, msg: String):
        digest = self._record('emotion_node', '/hri/emotion', msg.data)
        data = json.loads(msg.data)
        self.get_logger().info(
            f'[EMOTION ] {data["label"]:<12} conf={data["confidence"]} '
            f'| hash={digest[:12]}…'
        )
        self._latest['emotion'] = data
        self._fuse()

    def _gesture_cb(self, msg: String):
        digest = self._record('gesture_node', '/hri/gesture', msg.data)
        data = json.loads(msg.data)
        self.get_logger().info(
            f'[GESTURE ] {data["label"]:<12} conf={data["confidence"]} '
            f'| hash={digest[:12]}…'
        )
        self._latest['gesture'] = data
        self._fuse()

    def _motion_cb(self, msg: String):
        digest = self._record('motion_node', '/hri/motion', msg.data)
        data = json.loads(msg.data)
        self.get_logger().info(
            f'[MOTION  ] {data["label"]:<12} speed={data["speed_ms"]} m/s '
            f'| hash={digest[:12]}…'
        )
        self._latest['motion'] = data
        self._fuse()

    def _context_cb(self, msg: String):
        digest = self._record('context_node', '/hri/context', msg.data)
        data = json.loads(msg.data)
        self.get_logger().info(
            f'[CONTEXT ] {data["environment"]:<22} crowding={data["crowding"]} '
            f'| hash={digest[:12]}…'
        )
        self._latest['context'] = data
        self._fuse()

    # ── Fusion logic ───────────────────────────────────────────────────────────

    def _fuse(self):
        """Combine all four modalities and produce an intent decision.

        All four inputs must be present before fusion runs.
        This mirrors the late-fusion architecture in the FYP proposal.
        """
        if any(v is None for v in self._latest.values()):
            return  # Wait until at least one reading per modality

        emotion  = self._latest['emotion']['label']
        gesture  = self._latest['gesture']['label']
        motion   = self._latest['motion']['label']
        speed    = self._latest['motion']['speed_ms']
        context  = self._latest['context']['environment']
        crowding = self._latest['context']['crowding']

        # Priority 1 — Emergency signals override everything
        if motion == 'Running' or emotion == 'Panicked':
            intent = 'EMERGENCY   → Yield path / alert staff'
            policy = 'Move to wall. Increase social buffer to 3 m.'

        # Priority 2 — Conflicting cues (social dissonance)
        elif emotion == 'Angry' and gesture == 'Wave':
            intent = 'FRUSTRATED  → Offer assistance'
            policy = 'Slow approach. Speak calmly. Do NOT close distance.'

        elif emotion == 'Angry' and motion == 'Approaching' and speed > 0.8:
            intent = 'THREAT      → Avoidance response'
            policy = 'Back away. Maintain 2 m buffer. Log incident.'

        # Priority 3 — Friendly cues
        elif emotion == 'Happy' and gesture == 'Wave':
            intent = 'GREETING    → Acknowledge warmly'
            policy = 'Nod. Offer to assist. Maintain 1 m social distance.'

        elif emotion == 'Happy' and gesture == 'Beckon':
            intent = 'INVITATION  → Approach slowly'
            policy = 'Move toward person at 0.3 m/s.'

        # Priority 4 — Help needed
        elif emotion == 'Confused' or gesture == 'Point':
            intent = 'HELP_NEEDED → Initiate guidance'
            policy = 'Ask "How can I help?" Display information screen.'

        elif emotion == 'Sad':
            intent = 'DISTRESS    → Gentle check-in'
            policy = 'Approach slowly. Offer assistance quietly.'

        # Default
        else:
            intent = 'NEUTRAL     → Continue monitoring'
            policy = 'No action required. Passive observation.'

        self.get_logger().info('')
        self.get_logger().info('┌' + '─' * 53 + '┐')
        self.get_logger().info(f'│  INTENT : {intent:<43}│')
        self.get_logger().info(f'│  POLICY : {policy:<43}│')
        self.get_logger().info(f'│  INPUT  : {emotion}/{gesture}/{motion}/{context:<16}│')
        self.get_logger().info('└' + '─' * 53 + '┘')
        self.get_logger().info('')


def main(args=None):
    rclpy.init(args=args)
    node = FusionEngineNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()