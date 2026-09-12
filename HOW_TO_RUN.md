# How to Run AAGAAH (Quick Start Guide) 🌊🏔️

Running AAGAAH locally requires **2 PowerShell windows**:
- **PowerShell 1**: Runs the Python FastAPI backend (`http://127.0.0.1:8000`)
- **PowerShell 2**: Runs the React/Vite frontend dashboard (`http://localhost:5173`)

---

## ⚡ Terminal 1: Backend Server (FastAPI)

Open your **first PowerShell window** and run:

```powershell
# 1. Navigate to the aagaah project directory
cd D:\projects\SIH\aagaah

# 2. Activate Python Virtual Environment
# If your .venv is in the project root:
..\.venv\Scripts\Activate.ps1

# (Optional: If activating for the first time or setting execution policy)
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process

# 3. Set demo environment variables
$env:AAGAAH_DEMO_MEMORY="true"
$env:AAGAAH_SCHEDULE="true"
$env:AAGAAH_INTERVAL_SECONDS="15"

# 4. Start the FastAPI backend server
python -m uvicorn aagaah.main:app --app-dir backend-api --host 127.0.0.1 --port 8000
```

> ✅ **Verification**: You will see:
> `INFO: Uvicorn running on http://127.0.0.1:8000`  
> You can visit `http://127.0.0.1:8000/docs` to see the live API documentation.

---

## ⚡ Terminal 2: Frontend Dashboard (React + Vite)

Open your **second PowerShell window** and run:

```powershell
# 1. Navigate to the frontend directory
cd D:\projects\SIH\aagaah\frontend

# 2. (First time only) Install npm dependencies
# npm install

# 3. Launch the Vite development server
npm run dev
```

> ✅ **Verification**: You will see:
> `VITE v6.x ready in ... ms`  
> `➜ Local: http://127.0.0.1:5173/`

---

## 🌐 Open in Browser

Open your browser and navigate to:
```
http://localhost:5173
```

- The dashboard will load directly in **Live Operational Monitoring** mode.
- The 3D Map will automatically center on the **Mandakini River Catchment (Kedarnath Basin)**.
- All 7 river reaches will display live nominal telemetry.

---

## 💡 Quick Tips & Troubleshooting

1. **Port in use error (8000 or 5173)**:
   If a port is blocked from a previous run, find and terminate it:
   ```powershell
   # Find process using port 8000:
   Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | Select-Object OwningProcess
   # Stop process by ID:
   Stop-Process -Id <PID> -Force
   ```

2. **One-Liner Backend Startup**:
   If you want to run the backend in a single command line without separate `$env` commands:
   ```powershell
   python -c "import os, sys; os.environ['AAGAAH_DEMO_MEMORY']='true'; os.environ['AAGAAH_SCHEDULE']='true'; os.environ['AAGAAH_INTERVAL_SECONDS']='15'; import uvicorn; uvicorn.run('aagaah.main:app', app_dir='backend-api', host='127.0.0.1', port=8000)"
   ```

3. **Replay vs Live Mode**:
   - To test historical simulations, click **Replay** in the sidebar or click **Simulations** in the topbar.
   - To return to normal live monitoring, click **Exit Replay** in the topbar. All reaches will immediately reset to nominal baseline.
