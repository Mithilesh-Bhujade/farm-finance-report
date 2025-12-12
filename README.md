# Farm Finance Report

A FastAPI-based web application that generates a clean and professional **Farm Finance PDF Report**.  
Users fill out a simple web form with farmer details, crop data, expenses, and income entries.  
The system automatically calculates totals, generates a bar chart, and produces a downloadable PDF.

---

## 🚀 Features

### 🌾 **Farm Data Input**
- Farmer name  
- Crop name  
- Season (Kharif, Rabi, etc.)  
- Total acres  
- Sowing & harvest dates  
- Total production (optional)  
- Location (Village/Taluka/District/State)

### 💰 **Finance Data**
- Unlimited Expense entries  
- Unlimited Income entries  
- Auto-calculated:
  - Total Income  
  - Total Expense  
  - Profit / Loss  
  - Cost of cultivation per acre  

### 📊 **Chart & PDF**
- Matplotlib-generated "Income vs Expense" bar chart  
- Professionally formatted PDF using ReportLab  
- Header on every page:
  - GramIQ logo  
  - Dynamic title → `crop_acres_season_year`
  - Timestamp  
- Tables include:
  - Summary table  
  - Expense breakdown  
  - Income breakdown  
  - Ledger (sorted by date)  

---

## 📂 Project Structure
```
farm-finance-report/
│
├── app/
│   ├── main.py    
│   ├── chart.py 
│   ├── pdf_generator.py 
│   ├── schemas.py 
│   └── templates/
│       └── form.html 
│
├── static/
│   ├── logo.png 
│   └── chart.png  
│
├── .gitignore   
├── requirements.txt  
└── README.md   
```

---

## 📦 Libraries Used

| Library | Purpose |
|--------|---------|
| **FastAPI** | Web backend framework |
| **Uvicorn** | Development server |
| **Jinja2** | HTML form rendering |
| **ReportLab** | PDF creation |
| **Matplotlib** | Chart generation |
| **Pydantic** | Data validation |
| **python-multipart** | Form data handling |

---

## 🛠️ Setup Instructions (Windows)

### 1️⃣ Clone the repository
 - ```bash
   git clone https://github.com/<your-username>/farm-finance-report.git
   ```
 - ```bash
   cd farm-finance-report
   ```

### 2️⃣ Create and activate virtual environment
- Crate venv
  ```bash
  python -m venv venv
  ```
- Activate venv (Windows PowerShell)
  ```bash
  .\venv\Scripts\activate
  ```
- Or activate in Command Prompt (cmd.exe)
  ```bash
  .\venv\Scripts\activate
  ```

### 3️⃣ Install required packages
 - ```bash
   pip install --upgrade pip
   ``` 
 - ```bash
   pip install -r requirements.txt
   ```

### ▶️ Running the Application
- Start the FastAPI server:
```uvicorn app.main:app --reload```

- Then open the browser at:
```http://127.0.0.1:8000```

### ▶️ Usage Flow
- Fill out the farmer & crop details
- Add expenses & incomes
- Click Generate PDF
- PDF downloads automatically
- Open PDF → verify summary tables, ledger, and chart
