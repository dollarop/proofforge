# ProofForge Demo Script

Target length: 2:30-2:50.

## 0:00-0:20 - Problem

"Generative media is easy to create, but its history is easy to lose. A team receives an
image without a durable record of the model, prompt, parameters, evaluation, or exact
bytes that were approved. ProofForge keeps that chain intact."

## 0:20-0:55 - Brief

Open the deployed app. Show product, audience, core promise, tone, and format. Explain
that the structured brief becomes the shared input for every variant.

## 0:55-1:25 - Generation

Click **Generate campaign pack**. Point out the three variants, stable layout, quality
score, and accessibility alt text. Explain that the development mode is deterministic so
the complete workflow remains testable without consuming inference credits.

## 1:25-1:55 - Provenance

Open **Inspect canonical manifest**. Highlight run id, provider, model, prompt, parameters,
asset URI, byte size, and SHA-256 digest. Return to the app and show **Manifest verified**.

## 1:55-2:25 - Genblaze and B2

Show the architecture image. Explain that live mode uses Genblaze's
`GMICloudImageProvider`, falls back from Seedream to Gemini if needed, and passes the
result into an `ObjectStorageSink` backed by the private Backblaze B2 bucket. Assets and
manifests use a hierarchical per-run layout.

## 2:25-2:45 - Close

"ProofForge makes generated media inspectable, durable, and verifiable from brief to
bucket. Next, the same provenance-first workflow expands to audio and video campaign
packs."

## Recording checklist

- Browser zoom 100%, notifications disabled.
- Record 1080p landscape.
- Do not expose credentials, account email, bucket ids, or private dashboards.
- Use only the public app, public GitHub repository, and prepared architecture graphics.
- Keep the final video under three minutes.

