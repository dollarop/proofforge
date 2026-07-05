# ProofForge

ProofForge turns a campaign brief into evaluated media variants with a verifiable provenance record. Every output is SHA-256 bound to a canonical Genblaze manifest; live deployments persist assets and manifests to Backblaze B2.

## Why it exists

Creative teams need to know which model, prompt, parameters, and evaluation produced an asset. ProofForge makes that chain inspectable instead of leaving provenance in screenshots and chat history.

## Current capabilities

- Working campaign brief and variant gallery.
- Deterministic local media engine for zero-cost development and judging fallback.
- Genblaze `Run`, `Step`, and canonical `Manifest` generation.
- SHA-256 verification for every output asset.
- Quality score and accessibility alt text per variant.
- Responsive FastAPI application with no frontend build step.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Architecture

1. The API validates a structured campaign brief.
2. The generation engine creates multiple media variants.
3. An evaluator scores each output and marks weak variants for review.
4. Genblaze records provider, model, prompt, parameters, asset hash, and lineage.
5. Development mode writes locally; live mode uses an `ObjectStorageSink` backed by `S3StorageBackend.for_backblaze()`.

## Live configuration

Copy `.env.example` to `.env` and provide scoped credentials only in the deployment environment. Never commit keys. GMI Cloud is optional; the provider adapter is installed with `pip install -e ".[gmicloud]"`.

## Hackathon delivery checklist

- [x] Functional local app
- [x] Meaningful Genblaze provenance
- [x] Integrity verification
- [x] GMI Cloud generation adapter with model fallback
- [x] B2 durable object storage adapter
- [ ] Hosted judge URL
- [ ] Public repository
- [ ] Three-minute demo video
- [ ] Devpost submission
