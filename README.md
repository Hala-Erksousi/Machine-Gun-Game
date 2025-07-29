# Machine Gun Game
This project presents a robust real-time detection and tracking system utilizing multiple camera inputs, accompanied by a user-friendly Graphical User Interface (GUI). The system is designed to simultaneously process video streams from 
several cameras, accurately identify and track object movements, and display this information in a clear and simplified manner to the user. 

---
# Logo
![Machine Gun Game Logo](https://github.com/Hala-Erksousi/Machine-Gun-Game/blob/master/machine-gun-game-logo.png)

---
## About The Project
### How it works:

1.  **Camera Input:** Multiple cameras capture video streams simultaneously.
2.  **Object Detection & Tracking:** Software identifies and tracks moving objects in real-time from these video feeds.
3.  **GUI Display:** A user interface shows the camera feeds with detected objects and their paths.
4.  **Hardware Interaction :** Based on  user input, an Arduino board can control motors (e.g., servo, stepper) , enabling real-world actions.
---
### Technologies Used:

- **Python**
    - **OpenCV:** For real-time video processing, object detection, and tracking.
    - **PyQt5:** For creating the interactive Graphical User Interface.
    - **Threading:** To handle concurrent video stream processing.
- **Arduino (C++)**
    - **Servo Motor:** For firing the ball.
    - **Power Servo Motor:** For the loading process before firing.
    - **Stepper Motor:** For aiming the weapon and controlling its movement

---
## Getting Started

Using vscode to setup the enviroment to use this code.

### Prerequisites:

* Python 3.10
* Arduino IDE 
* Webcams connected to your computer.
* OpenCV library
* NumPy library
* Mediapipe library
* PyQt5 library
* pyserial library

### Downloading the Project:
1.Clone the repository:
    ```
    git clone https://github.com/Hala-Erksousi/Machine-Gun-Game.git
    ```
    
2.Upgrade pip (if necessary): pip install --upgrade pip

3.Install the required packages: pip install opencv-python numpy mediapipe pyserial pyQt5

4.Upload the Arduino sketch

5.Run the main script: python MainApp.py

---
## Features
* ✔ Real-time detection and tracking from multiple cameras.
* ✔ Intuitive GUI for easy control and monitoring.
* ✔ Concurrent processing of video streams using threading.
* ✔ **Hardware Control:** Integration with Arduino for controlling servo and stepper motors based on physical inputs.

---
## Contributing
We believe in the power of collaboration and the open-source spirit! Your insights and contributions are what truly bring projects like this to life. Whether it's a brilliant new feature, a clever optimization, or a keen eye for a bug, your efforts are immensely valued 

Ready to make your mark?

1.  Fork the repository:
2.  Create your Feature Branch: (`git checkout -b feature/your-awesome-contribution`)
3.  Commit your Changes: (`git commit -m 'Add an Amazing new Feature'`)
4.  Push to the Branch: (`git push origin feature/your-awesome-contribution`)
5.  Open a Pull Request: Let's discuss your fantastic work and merge it into the main project.

If you have an idea but prefer not to code it yourself, feel free to open an issue with the tag "enhancement". We're always eager to hear your thoughts!

And if you love what we're doing, a simple star on the repository goes a long way in showing your support. Thank you for being a part of this journey!


---
## Contact

For any questions, suggestions, or contributions, feel free to reach out!

 **Email1:** halaerksousi@gmail.com     
 **Email2:** sana.2522005@gmail.com  
 **Email3:** msallamsalam4@gmail.com  



