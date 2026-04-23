#!/bin/bash

# -------------------------------
# Base query (NO limit here!)
# -------------------------------
MYBIGQUERY='files from dune:all where core.file_type=detector and core.run_type=hd-protodune and core.data_tier=full-reconstructed and core.data_stream=physics and core.runs[any]=28759'


# -------------------------------
# Chunk configuration
# -------------------------------
CHUNK_SIZE=5000          # max files per workflow
CHUNK_INDEX=${1:-0}      # pass 0,1,2,... when running script
SKIP=$((CHUNK_INDEX * CHUNK_SIZE))

# Construct final MQL
MQL_QUERY="$MYBIGQUERY ordered skip ${SKIP} limit ${CHUNK_SIZE}"

echo "Submitting chunk ${CHUNK_INDEX}"
echo "MQL = $MQL_QUERY"


# ---------------------
# Job settings
# ---------------------
JOBSCRIPT="./michelData_10sPerJob.jobscript"
FILES_PER_JOB=10


# ---------------------
# Output destination (WebDAV scratch)
# ---------------------
# IMPORTANT: Use HTTPS WebDAV door for dCache scratch, NOT /pnfs/...
# JustIN wrapper will upload matching outputs after your jobscript finishes. :contentReference[oaicite:2]{index=2}
WEBDAV_SCRATCH_DIR="https://fndcadoor.fnal.gov:2880/dune/scratch/users/szh2/pdhd_DATA_Michel/beamRun_28759/"



# --------------------
# Submit workflow
# --------------------
justin simple-workflow \
--mql "$MQL_QUERY" \
--jobscript "$JOBSCRIPT" \
--max-distance 9999 \
--rss-mib 4000 \
--scope usertests \
--env "FILES_PER_JOB=${FILES_PER_JOB}" \
--output-pattern "michelt0_decon_*.root:${WEBDAV_SCRATCH_DIR}" \
--lifetime-days 1 \
--classad 'DESIRED_Sites="US_FNAL-FermiGrid"'


#--env "NUM_EVENTS=3" \