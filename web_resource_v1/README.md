# AMP Evidence Atlas v1 RC1 Local Preview

This is a local-only minimal website/API for `releases/amp_evidence_atlas_v1_rc1`.
It uses only the Python standard library and streams large TSV files on demand.

## Run

```bash
cd /root/work/抗菌肽/数据库/batch/4-team
python web_resource_v1/server.py --host 127.0.0.1 --port 8989
```

Open:

```text
http://127.0.0.1:8989
```

## API Smoke Checks

```bash
curl -s http://127.0.0.1:8989/api/v1/releases | python -m json.tool >/dev/null
curl -s 'http://127.0.0.1:8989/api/v1/search?q=DBAASPS_18493&status=source_conflict&limit=3' | python -m json.tool
curl -s http://127.0.0.1:8989/api/v1/downloads | python -m json.tool
curl -s http://127.0.0.1:8989/api/v1/schemas | python -m json.tool
```

## Guardrails

- This preview does not redistribute PDFs, XML full text, images, or supplementary files.
- Non-source-verified rows are evidence discordance/provenance gaps, not automatic database errors.
- `accepted_with_cautions` is not clean.
- The package remains `release_package_candidate_not_public_nar_submission_ready` until public hosting, license review, and manual stratified validation are complete.
