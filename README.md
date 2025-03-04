# 🖥️ Computer Vision Project

This repository contains two main functionalities:
1. **Gaze Tracking** - Detects and tracks the user's eye movement and direction.
2. **Ad Region of Interest (ROI)** - Detects faces and marks specific regions where advertisements could be placed.

---

## 📌 Features

✔️ **Real-time gaze tracking** using a webcam  
✔️ **Detects where a person is looking** (left, right, up, down, center)  
✔️ **Blinks detection** using Eye Aspect Ratio (EAR)  
✔️ **Face and Ad Region Detection** using Dlib and OpenCV  
✔️ **Customizable settings for both modules**  

---

## 🚀 **Installation**

### **1️⃣ Clone the Repository**
```bash
git clone -b ad_region_of_interest https://github.com/ayayasminebelloum/Computer-Vision.git --single-branch
cd Computer-Vision

2️⃣ Create a Virtual Environment

python -m venv venv

3️⃣ Activate the Virtual Environment

# Mac / Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate

4️⃣ Install Dependencies

pip install -r requirements.txt

🎯 How to Run the Project

1️⃣ Run Gaze Tracking

Detects where a user is looking in real-time using a webcam.

python example.py

➡️ Expected Output
	•	Displays the eye coordinates, gaze direction, and whether the person is blinking.
	•	Detects left, right, up, down, and center gaze.

2️⃣ Run Ad Region of Interest (ROI)

Detects faces and marks regions where advertisements can be placed.

python AdRegionOfInterest.py

➡️ Expected Output
	•	Draws a bounding box around detected faces.
	•	Marks Ad Regions dynamically.

🎥 Run with a File Instead of Webcam

python AdRegionOfInterest.py "AdImages/PHOTO-2025-03-02-09-10-01.jpg"

🛠 Troubleshooting

Issue	Solution
Black screen on webcam?	Ensure your webcam is working (python -m cv2)
Gaze detection incorrect?	Adjust lighting conditions or camera angle
Dlib not found?	Run pip install dlib opencv-python
Webcam lagging?	Reduce video frame size in code

📌 Project Structure

📂 Computer-Vision
├── 📂 gaze_tracking        # Gaze tracking module
├── 📂 AdImages             # Image dataset for Ad ROI
├── 📜 example.py           # Runs gaze tracking
├── 📜 AdRegionOfInterest.py # Runs Ad ROI detection
├── 📜 requirements.txt      # Dependencies
├── 📜 README.md             # Documentation

👨‍💻 Contributing

@ayayasminebelloum & @makiwarner & @inds123

📜 License

This project is licensed under MIT License. Feel free to use and modify.

