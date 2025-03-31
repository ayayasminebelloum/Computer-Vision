Here’s a clean, corrected, and complete version of your README.md, tailored specifically to your version of the Computer Vision project with gaze tracking, ad + heatmap, and fullscreen UI logic.

⸻



# 🖥️ Computer Vision Project

This project provides a real-time **gaze tracking system** and a visual analytics interface for measuring user attention on **ads** via heatmaps. It also includes calibration and live webcam gaze visualization, built with OpenCV, Dlib, and a fullscreen UI.

---

## 📌 Features

✔️ Fullscreen OpenCV GUI with custom button interaction  
✔️ **Real-time gaze tracking** with a webcam  
✔️ **Calibration module** to improve accuracy  
✔️ Live **gaze visualization** on screen (camera mode)  
✔️ Watch **ad videos or images** and generate **gaze heatmaps**  
✔️ Eye direction detection using `dlib` and `GazeTracking`  
✔️ Disable ad/camera until calibration is complete

---

## 🚀 Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/computer-vision.git
cd computer-vision

2️⃣ Create a Virtual Environment

python3.11 -m venv venv
source venv/bin/activate

✅ Make sure you’re using Python 3.11 (not 3.13).

3️⃣ Install Dependencies

pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

If dlib fails to install, follow instructions below in 🛠 Troubleshooting.

⸻

🎯 How to Run the Project

🧠 Main App: Gaze Tracker + Ad Heatmap

python src/main.py

	•	Navigate using the fullscreen interface
	•	Calibrate before using the camera or ads
	•	Watch ads and generate gaze-based heatmaps

⸻

🗂️ Project Structure

📂 computer-vision/
│
├── venv/                     # Virtual environment
├── requirements.txt          # Python dependencies
│
├── src/
│   ├── main.py               # Main application logic
│   ├── gaze_tracking/        # GazeTracking module
│   ├── ad_tracking/
│   │   ├── calibrate.py      # Calibration routine
│   │   ├── camera.py         # Live gaze visualization
│   │   ├── ad.py             # Show ad and generate heatmap
│   ├── utils/
│   │   └── ui_utils.py       # Fullscreen UI rendering
│   ├── data/
│   │   ├── ad1.jpg … ad9.jpg # Sample ad images



⸻

🎥 Run with a Specific Ad Image

python src/main.py

➡️ Use the UI to select an ad and generate the heatmap.

⸻

🛠 Troubleshooting

Issue	Solution
ModuleNotFoundError: cv2	Run pip install opencv-python
dlib fails to install	Use Python 3.11 and run: brew install cmake && pip install dlib
Webcam shows black screen	Try changing lighting, or test with python -m cv2
Gaze not accurate	Re-run calibration, adjust distance or lighting



⸻

👨‍💻 Contributors
	•	@ayayasminebelloum
	•	@makiwarner
	•	@inds123
	•	@shahafbr

⸻

📜 License

This project is licensed under the MIT License.
Feel free to use, share, and modify with credit.

Let me know if you want this turned into a downloadable `README.md` file, or if you want to include screenshots, example outputs, or demo videos.

