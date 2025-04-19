from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nse_utils import download_nse_bhavcopy, filter_equity_stocks, detect_patterns

app = FastAPI()

# Allow your frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://www.liteamc.com"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/screener")
def run_screener():
    try:
        df = download_nse_bhavcopy()
        df = filter_equity_stocks(df)
        patterns = detect_patterns(df)
        return patterns
    except Exception as e:
        return {"error": str(e)}
