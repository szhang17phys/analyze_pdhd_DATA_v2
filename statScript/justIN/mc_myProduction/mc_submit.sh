#!/bin/bash


# --------------------------------
# Monte Carlo configuration
# --------------------------------
N_JOBS=5            # total number of justIN jobs
EVENTS_PER_JOB=${EVENTS_PER_JOB:-10}

echo "Submitting MC workflow"
echo "N_JOBS         = ${N_JOBS}"
echo "EVENTS_PER_JOB = ${EVENTS_PER_JOB}"



# ---------------------
# Job settings
# ---------------------
JOBSCRIPT="./pdhd_mc_chain.jobscript"


# ---------------------
# Output destination (WebDAV scratch)
# ---------------------
# IMPORTANT: Use HTTPS WebDAV door for dCache scratch, NOT /pnfs/...
# JustIN wrapper will upload matching outputs after your jobscript finishes. :contentReference[oaicite:2]{index=2}
WEBDAV_SCRATCH_DIR="https://fndcadoor.fnal.gov:2880/dune/scratch/users/szh2/MC_pdhd_Michel/my2026_production/"




# --------------------------------
# Submit workflow
# --------------------------------
justin simple-workflow \
    --monte-carlo "${N_JOBS}" \
    --jobscript "${JOBSCRIPT}" \
    --rss-mib 4000 \
    --scope usertests \
    --env "EVENTS_PER_JOB=${EVENTS_PER_JOB}" \
    --output-pattern "cosmic_detsim_stage2_*.root:${WEBDAV_SCRATCH_DIR}" \
    --lifetime-days 1 \
    --classad 'DESIRED_Sites="US_FNAL-FermiGrid"'




# --------------------
# Submit workflow
# --------------------
# justin simple-workflow \
# --mql "$MQL_QUERY" \
# --jobscript "$JOBSCRIPT" \
# --max-distance 9999 \
# --rss-mib 4000 \
# --scope usertests \
# --env "FILES_PER_JOB=${FILES_PER_JOB}" \
# --output-pattern "michelt0_decon_*.root:${WEBDAV_SCRATCH_DIR}" \
# --output-pattern "mcTruth_*.txt:${WEBDAV_SCRATCH_DIR}" \
# --lifetime-days 1 \
# --classad 'DESIRED_Sites="US_FNAL-FermiGrid"'

#--env "NUM_EVENTS=3" \