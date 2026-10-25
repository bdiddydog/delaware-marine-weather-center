# Delaware Marine Weather Center

Automated NOAA marine chart dashboard focused on Delaware Bay, Delaware Atlantic waters, and Chesapeake Bay.

## How it works
- GitHub Actions checks NOAA products on a schedule.
- NOAA OPC charts are loaded directly from official URLs with a retrieval timestamp.
- NWS marine-zone forecast text, NWS active alerts, and NDBC buoy observations are retrieved server-side and stored as `data/latest.json`.
- The website displays only these official data products. **No AI-written forecast discussions are published automatically.**
- Draft forecasting discussion work stays outside this public site unless deliberately published.

## Activate
1. In repository Settings → Pages, choose GitHub Actions as the build/deployment source.
2. Go to Actions → Marine NOAA Update → Run workflow.
3. Check the workflow completes successfully and open the Pages URL.

GitHub Pages is public. Do not commit private notes or subscriber data.
NOAA source issue/valid times take precedence over site update timestamps; always check official warnings before boating.
