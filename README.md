# Edge-Based Palm & Hand Geometry Authentication System

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-009688.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10+-red.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)

A highly accurate, modular, and real-time biometric verification system built for edge devices. This platform uses only a standard RGB webcam (no infrared or depth sensors required) to authenticate users based on their unique hand and palm geometry.

Unlike heavy deep-learning biometric models, this system leverages pure geometric mathematical embeddings (distance, ratio, angular, and statistical features) extracted via MediaPipe landmarks. This makes it incredibly fast, completely offline-capable, and optimized for low-end CPUs.

---

## Key Features

- **Geometric Biometric Embeddings**: Extracts a robust 20-50 dimensional feature vector using distances between fingertips, palm width ratios, and joint angles.
- **Scale & Depth Invariant**: Hand landmarks are normalized to the wrist origin and scaled by palm width, ensuring your hand can be closer or further from the camera without failing.
- **Enterprise UI / UX**: A premium Glassmorphism-themed Single Page Application (SPA) featuring a dynamic scanning reticle, sweeping laser animations, and responsive toast notifications.
- **Admin Dashboard & Approvals**: A secure, token-protected portal where administrators can view all registered users, their categorized roles (Student, Teacher, etc.), and instantly Approve or Reject their biometric access.
- **Secure by Design**: Raw images are processed entirely in memory and immediately discarded. Only irreversible mathematical embeddings are stored in the SQLite database.

---

## Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Computer Vision**: OpenCV, MediaPipe Hands
- **Math / Vectorization**: NumPy, Python Math
- **Database**: SQLite
- **Frontend**: HTML5, Vanilla JS, Vanilla CSS, Lucide Icons

---

## Getting Started (Local Development)

### Prerequisites
- Python 3.10 or higher
- A working webcam

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd "YOUR_REPO_NAME"
```

### 2. Create a Virtual Environment & Install Dependencies
```bash
python -m venv .venv
# Activate on Windows:
.\.venv\Scripts\activate
# Activate on Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Run the Application
```bash
uvicorn main:app --reload
```
Once the server starts, open your browser and navigate to: **http://127.0.0.1:8000**

---

## How to Use the System

### As a User (Registration & Verification)
1. At the Landing Page, select **User Scanner**.
2. Enter your desired Username/ID and select your **Category** (e.g., Student).
3. Place your hand within the scanning reticle and click **Request Registration**. 
4. The system will capture a 5-frame burst to create an averaged, highly accurate geometric profile. Your status will now be `PENDING`.
5. *(You cannot authenticate until an Admin approves your registration).*

### As an Admin (Approval Workflow)
1. At the Landing Page, select **Admin Portal**.
2. Log in using the default credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
3. View the Dashboard data table to see all pending requests and their requested categories.
4. Click the Green Checkmark (`✓`) to **Approve** a user.
5. The approved user can now return to the User Scanner and successfully authenticate!

---

## Sharing via GitHub (For Other Users)

If you want to share this project so that other users can run it on their machines, you can push the code to a GitHub repository.

### 1. Push your code to GitHub:
Open your terminal in the project folder and run:

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### 2. How others can use it:
Once your code is on GitHub, anyone can use your project by following the **Getting Started (Local Development)** instructions above. They simply need to:
1. Run `git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git`
2. Set up their Python virtual environment.
3. Install `requirements.txt`.
4. Run `uvicorn main:app`.

Because this system uses a local SQLite database (`biometrics.db`), all data will be saved safely on their own machine.

---

## Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
