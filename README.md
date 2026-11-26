# SENTINEL

SENTINEL reviews security findings supplied by an authorized scanner. Its Red
agent assesses the evidence, its Blue agent proposes defensive remediation, and
its Judge agent compares both reports against the original evidence.

The web app does **not** scan websites, connect to target systems, or execute
probes. Run a scanner you are authorized to use separately, then paste or upload
its finding for analysis.

## Requirements

- Python 3.10 or later
- Ollama running locally
- A model available in Ollama (defaults to `llama3.2:3b`)

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull llama3.2:3b
python -m uvicorn app:app --reload
```

<img width="1228" height="708" alt="image" src="https://github.com/user-attachments/assets/9526a468-33a4-473c-b393-e0e085200f73" />
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) for the product overview,
then select **Start Security Scan** to open the review workspace at `/review`.

flowchart TD
    A["User / Browser"] --> B["Frontend: HTML, CSS, JavaScript"]
    B -->|"POST /api/reviews"| C["FastAPI Web Server"]
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/ae003ebb-5b70-4236-bc43-a03755a9d70b" />


If Ollama is not running or the model is unavailable, the review endpoint
returns a clear service error and the interface lets you retry after fixing it.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server address |
| `SENTINEL_MODEL` | `llama3.2:3b` | Model used by all three agents |

For example, set these in PowerShell before starting the app:

```powershell
$env:OLLAMA_HOST = "http://localhost:11434"
$env:SENTINEL_MODEL = "llama3.2:3b"
```

## Use

1. Run a security scanner against a system you are authorized to assess.
2. Paste its finding or choose a text, log, or JSON file in SENTINEL.
3. Review the Red, Blue, and Judge agent reports.
4. Export the combined evidence and analysis as a Markdown report.

Reviews are processed by the configured Ollama server. SENTINEL does not save
them on the server. Recent reports are kept in the current browser tab's
`sessionStorage` and are removed when that tab closes; use **Clear** to remove
them sooner. Avoid entering secrets or personal data into scanner evidence.

AI output is advisory, may be wrong, and should be checked against the original
system and evidence before acting.

## API

`POST /api/reviews` accepts a JSON body containing a `finding` string between
20 and 20,000 characters. It returns a review ID, timestamp, and the three
agent reports. Interactive API documentation is available at
`/docs` while the local server is running.

## Tests

```powershell
python -m unittest discover -s tests -v
```
