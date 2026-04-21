# Sequential Gesture Recognition for ROS2 using MediaPipe

Builds upon ROS2 MediaPipe Suite by PME26Elvis (https://github.com/PME26Elvis/mediapipe_ros2_suite/) and was designed to work using the full Hand Landmarker and Gesture Recognizer model .task files provided by Google AI Edge:
https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer
https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker


> ROS2 Humble on Ubuntu 22.04 (WSL)

---

This node can recognize the following gesture sequences (individual gestures from the MediaPipe Gesture Recognizer Model)
||
|---|
| `'Open palm', 'Pointing up'` |
| `'Open palm', 'Victory'` |
| `'Closed fist'` |
| `'Thumb down', 'Thumb up'` |
| `'Thumb up', 'Closed fist', 'Closed fist'` |
| `'Thumb down', 'Closed fist', 'Pointing up'` |
| `'Thumb down', 'Victory', 'Thumb down'` |
| `'Pointing up', 'Closed fist', 'Thumb up', 'Thumb up'` |
| `'Pointing up', 'Open palm', 'Open palm', 'Victory', 'Thumb up'` |
| `'Victory', 'Open palm', 'Thumb down', 'Pointing up', 'Victory'` |
| `'I Love You'` |

---

## Installation
1) Install ROS2 MediaPipe Suite by PME26Elvis (https://github.com/PME26Elvis/mediapipe_ros2_suite)\
      1.1) Recommended to use the MediaPipe full Hand Landmarker and Hand Gesture Classifier modles (found here: ai.google.dev/edge/mediapipe/solutions/),
           this node was made using them and relies on the gestures defined in them.
2) Install and build this node:
   ```
   cd ~/ros2_ws/src
   git clone https://github.com/Polkky/sequentialgesturerecognitionROS2
   cd ..
   colcon build
   source install/setup.bash
   ```
3) Run the image feed and MediaPipe Suite
   ```
   ros2 run v4l2_camera v4l2_camera_node  # or some other camera that publishes to /image_raw

   # New terminal, remember to source it
   ros2 launch mediapipe_ros2_py mp_node.launch.py start_rviz:=true
   ```
4) Run the sequence recognition node
   ```
   # New terminal
   ros2 run gr_sequence sequence_node
   
   # Optional: echo the topic in a new terminal, also recommended to echo the gesture recognizer topic from the Suite in a separate window
   ros2 topic echo /gesture_sequence
   ```
