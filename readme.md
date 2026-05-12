# 🏓 Table Tennis Tournament Organizer

Web-based system developed in **Django** for complete management of table tennis tournaments, including player registration, tournament organization, match generation, and match tracking.

---

## 🚀 Features

* 📌 Championship registration
* 👥 Participant registration
* 🏆 Ranking system
* 🔀 Automatic round generation (Swiss System)
* 🎯 Elimination phases (knockout)
* 📊 Match results control
* 📺 Bracket visualization
* 🧠 Automatic match organization
* 🔎 Standings consultation (overall classification)

---

## 🧱 Technologies Used

* 🐍 Python 3.x
* 🌐 Django
* 🗄️ SQLite (default, can be migrated to PostgreSQL)
* 🎨 HTML + CSS + Bootstrap
* ⚙️ JavaScript (for interactions and visualization) (keys)

---

## 📁 Project Structure

```
organizer-championships-tt/
│
├── core/ # Main app (tournaments, logic)
├── users/ # Authentication and users
├── static/ # Static files (CSS, JS)
├── templates/ # HTML templates
├── db.sqlite3 # Database
├── manage.py
└── README.md
```

---

## ⚙️ How to run the project

### 1. Clone the repository

```bash
git clone https://github.com/marcoantonio567/organizador-campeonatos-tt.git cd organizar-campeonatos-tt


### 2. Create a virtual environment

```bash
python -m venv venv

```

Activate:

* Windows:

```
bash venv\Scripts\activate
```

* Linux/Mac:

```
bash source venv/bin/activate
```

---

### 3. Install dependencies

```
bash pip install -r requirements.txt
```

---

### 4. Run migrations

```
bash python manage.py migrate
```

---

### 5. Create a superuser

```
bash python manage.py createsuperuser
```

---

### 6. Run the server

```bash
python manage.py runserver
```

Access in your browser:

```
http://127.0.0.1:8000/
```

---

## 🧠 System Rules

### Swiss System

* Players face opponents with similar performance
* Avoids repeated matches
* Cumulative scoring

### Elimination Phase

* Ranking of the best Swiss players
* Knockout format matches
* Champion determination

---

## 📊 Modeling (Summary)

* **Championship**
* **Player**
* **Match**
* **Round**
* **Ranking**

---

## 🎯 Project Objective

This system was developed For:

* Facilitating the organization of local championships
* Automating brackets and matchups
* Improving the tournament management experience
* Serving as a foundation for larger projects (tournament SaaS)

---

## 🔮 Possible future improvements

* 📱 Responsive mobile interface
* 📡 REST API with Django Rest Framework
* 🏅 Player history system
* 📈 Advanced statistics
* 🎥 Integration with large screen (match display)
* ☁️ Cloud deployment (AWS / Render)

---

## 🤝 Contribution

Contributions are welcome!

1. Fork the project
2. Create a branch (`git checkout -b feature/nova-feature`)
3. Commit (`git commit -m 'feat: nova feature'`)
4. Push (`git push origin feature/nova-feature`)
5. Open a Pull Request
