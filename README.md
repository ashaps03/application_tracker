# 📌 application_tracker

A smart-ish job application tracker that auto-fills jobs using Gmail parsing and lets you manage them in a clean dashboard.

---

## 🛠️ Tech Stack

- **Frontend:** React (Vite)
- **Backend:** Flask (Python)
- **Database:** SQLite
- **Email Parsing:** Gmail API 

---

## 🔧 Setup Instructions

### Clone the Repository

```bash
git clone https://github.com/ashaps03/application_tracker.git
cd application_tracker
```

### 🚨 Switch to your assigned branch

Before making changes, switch to your designated branch:

```bash
git fetch
git switch <your-branch-name>   # e.g., ash-dev or bella-dev
```

---

## 🖥️ Backend Setup (Flask)

### Navigate to the backend folder

```bash
cd server
```

### Create and activate virtual environment

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the Flask server

```bash
python main.py
```

> Server runs on: `http://127.0.0.1:8080`

---

## 🌐 Frontend Setup (React + Vite)

### Open a new terminal and go to the frontend folder

```bash
cd ../job-tracker-frontend
```

### Install dependencies

```bash
npm install
```

### Run the React app

```bash
npm run dev
```

> App runs on: `http://localhost:5173`