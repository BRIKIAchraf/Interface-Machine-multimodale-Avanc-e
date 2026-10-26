# Multimodal Human-Machine Interface

Computer-vision and speech prototype combining gestures, voice commands and facial-expression signals to create a natural human-machine interaction loop.

## Product concept

The interface observes multiple input channels, normalizes them and applies explicit fusion rules to select an action.

~~~text
Webcam → gesture detector ─┐
Microphone → speech recognizer ─┼→ fusion engine → UI/system action
Face image → expression detector ─┘
~~~

## Implemented capabilities

### Gesture recognition

- skin-colour segmentation and contour analysis with OpenCV;
- convex-hull and convexity-defect analysis;
- detection of closed fist, open hand, pointing finger, victory sign and finger counts;
- real-time overlay on the video stream.

### Speech recognition

- French speech commands with SpeechRecognition;
- continuous listening in a background thread;
- ambient-noise adjustment and live transcription;
- commands for navigation, volume and display mode.

### Facial-expression signals

- face detection with Haar cascades;
- smile-based happy signal;
- neutral, sad and angry heuristic signals;
- visual feedback in the interface.

### Multimodal fusion

Examples of explicit rules:

- pointing finger + “ouvre” or “sélectionne” → selection;
- “mode sombre” / “mode clair” → display mode;
- closed fist → pause/stop;
- victory sign → confirmation;
- angry signal + closed fist → user-alert signal.

## Technology stack

Python · OpenCV · NumPy · PyQt6 · SpeechRecognition · PyAudio · Haar Cascades · multithreading

## Quick start

~~~bash
pip install -r requirements.txt
python main.py
~~~

A webcam and microphone are required. Good lighting and a clear background improve gesture and expression detection.

## Project structure

~~~text
src/gestures/    Hand tracking and gesture analysis
src/voice/       Speech recognition
src/emotions/    Facial-expression signals
src/fusion/      Multimodal decision rules
src/ui/          Main window and feedback
src/utils/       Video and voice worker threads
~~~

## Limitations

The current approach is a prototype based on heuristics. Skin-colour segmentation, Haar cascades and speech recognition can be sensitive to lighting, camera angle, accents, noise and bias. Production use would require stronger models, confidence scores, calibration, privacy controls and user-consent flows.

## Author

**Achraf BRIKI** · [LinkedIn](https://www.linkedin.com/in/achrafbriki/) · [Portfolio](https://achrafbriki.com)
