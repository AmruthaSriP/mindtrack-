# 🧘 Mind Track+ | Smart Mood & Stress Advisor

Mind Track+ is a lightweight, responsive web application designed to help users track their daily emotional well-being and stress levels. By logging mental states alongside daily activities, the app maps out behavioral trends to help users identify which habits bring them joy and which ones cause stress.

---

## 🚀 Features

* **Smart Dashboard:** View real-time stats including your total number of logs, average mood score (1-5), and average stress levels (1-10).
* **Easy Logging:** A simple, intuitive form with range sliders to quickly log your mood, stress level, activities, and personal thoughts.
* **14-Day Trend Charts:** Automatically generates a visual line graph using Matplotlib to compare your mood and stress scores over the last two weeks.
* **Activity Correlation Matrix:** Analyzes your top 5 most logged activities and ranks them by their average mood and stress outcomes.
* **Persistent Local Storage:** Saves all your history safely inside a local `mood_data.csv` file—no complex database configuration required.

---

## 🛠️ Tech Stack

* **Backend:** Python 3, Flask (Web Framework)
* **Data & Analytics:** Pandas, NumPy, Matplotlib (Data Analysis & Visualization)
* **Frontend:** HTML5, Tailwind CSS (Modern, Responsive Styling)

---

## 📦 Project Structure

```text
Mind-Track/
├── app.py                # Main Flask application and analysis logic
├── mood_data.csv         # Local data store (automatically generated)
└── templates/
    └── index.html        # Single-file dynamic Jinja2 template
