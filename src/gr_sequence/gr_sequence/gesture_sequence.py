"""
This node subscribes to the topic /mediapipe/hand/gestures and adds gestures to a sequence.
If the sequence matches one found in defined_sequences, it is published to the topic /gesture_sequence.
The published message contains three pieces of information: instruction, gestures and score.
Instruction could be used to direct a robot. Gestures retells the sequence (in order). Score tells the
mean "accuracy" of the gestures.
"""

import rclpy
from rclpy.node import Node
from mediapipe_ros2_interfaces.msg import HandGesture
from collections import deque
from gr_sequence_msgs.msg import Sequence

# Default mediapipe task has 7 gestures: None (invalid, unused), Closed_Fist, Open_Palm, Pointing_Up, Thumb_Down
# Thumb_Up, Victory, ILoveYou (reserved for 'Stop')
defined_sequences = {
    "Bring item no. 1 to me": ["Open_Palm", "Pointing_Up",],
    "Bring item no. 2 to me": ["Open_Palm", "Victory",],
    "Take held item to target": ["Closed_Fist"],
    "Inspect held item": ["Thumb_Down", "Thumb_Up"],
    "Approve inspection and send to assembly": ["Thumb_Up","Closed_Fist","Closed_Fist"],
    "Decline inspection and send to repair": ["Thumb_Down","Closed_Fist","Pointing_Up"],
    "Decline inspection and discard": ["Thumb_Down","Victory","Thumb_Down"],
    "Deliver item no. 1 to assembly continuously": ["Pointing_Up","Closed_Fist","Thumb_Up","Thumb_Up"],
    "Move to assembly for component assistance": ["Pointing_Up", "Open_Palm", "Open_Palm","Victory", "Thumb_Up"],
    "Move to assembly and check for discarded components": ["Victory","Open_Palm","Thumb_Down","Pointing_Up","Victory"]
}

# weighted mean for calculating the score of a gesture in a sequence since
# we take multiple recognized gestures. initial and end scores are dampened due to possibly lower-than-normal
# scores from the person's hand still forming the "final" or next gesture
def weighted_mean(tuple_list):
    sum = 0.0
    weight = 0.0
    for i in range(len(tuple_list)):
        if (i < 9) or (i > (len(tuple_list) - 6)):
            w = 0.3
        else:
            w = 1.0
        weight += w
        sum += tuple_list[i][1]*w

    return sum/weight

class GestureSequence(Node):
    def __init__(self):
        super().__init__('gr_sub')
        self.sequence = []
        self.gr_memory = deque(maxlen=25)  # 25 latest are kept in memory
        self.timestamp = self.get_clock().now().nanoseconds
        
        self.subscription = self.create_subscription(
            HandGesture,
            '/mediapipe/hand/gesture',
            self.gesture_callback,
            10
        )

        self.publisher = self.create_publisher(
            Sequence,
            '/gesture_sequence',
            10
            )
        self.timer = self.create_timer(0.2, self.publish_sequence)

        self.get_logger().info("Subscriber started, listening to the topic /mediapipe/hand/gesture")

    def gesture_callback(self, msg):
        gesture = msg.gesture
        score = msg.score
        self.timestamp = self.get_clock().now().nanoseconds     # timestamp for timers

        self.gr_memory.append((gesture,score))
        if len(self.gr_memory) == 25:
            entries = [i[0] for i in self.gr_memory]
            if len(set(entries)) == 1:
                if self.gr_memory[24][0] == "None":
                    self.gr_memory.clear()
                    self.get_logger().info("Invalid gesture not added to sequence")
                    return
                elif self.gr_memory[24][0] == "ILoveYou":
                    pub_msg = Sequence()
                    pub_msg.instruction = "Stop"
                    pub_msg.gestures = [entries[24]]
                    pub_msg.score = weighted_mean(self.gr_memory)
                    self.publisher.publish(pub_msg)
                    self.gr_memory.clear()
                    self.sequence.clear()
                    self.get_logger().info("'Stop' gesture published")
                else:
                    self.sequence.append((self.gr_memory[24][0],weighted_mean(self.gr_memory)))
                    self.gr_memory.clear()
                    sequence_gestures = [i[0] for i in self.sequence]
                    self.get_logger().info(f"Current sequence:  {sequence_gestures}")
    
    # attempt to publish every 2 seconds
    # also handles inactivity if inactive for 3 seconds
    def publish_sequence(self):
        now = self.get_clock().now().nanoseconds
        if ((now - self.timestamp) > 2*1e9) and (len(self.sequence) > 0):
            sequence_gestures = [i[0] for i in self.sequence]
            if sequence_gestures in defined_sequences.values():
                pub_msg = Sequence()
                key = next(k for k, v in defined_sequences.items() if v == sequence_gestures)
                pub_msg.instruction = key
                pub_msg.gestures = sequence_gestures
                pub_msg.score = sum(s for _,s in self.sequence)/len(self.sequence)
                self.publisher.publish(pub_msg)
                self.get_logger().info(f"Sequence {self.sequence} was valid and published as '{key}'")
                self.gr_memory.clear()
                self.sequence.clear()
            elif ((now - self.timestamp) > 3*1e9):
                self.gr_memory.clear()
                self.sequence.clear()
                self.get_logger().info("Sequence cleared due to inactivity (sequence not found)")
        


def main(args=None):
    rclpy.init(args=args)
    gr_seq = GestureSequence()
    rclpy.spin(gr_seq)
    gr_seq.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
