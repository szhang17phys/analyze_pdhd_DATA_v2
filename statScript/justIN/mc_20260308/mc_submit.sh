#!/bin/bash

# -------------------------------
# Base query (NO limit here!)
# -------------------------------
#MYBIGQUERY="files from hd-protodune:hd-protodune__pdhd_mc_2025a__full-reconstructed__10_10_04d01__standard_reco_protodunehd_MC__pdhd_5GeV_h4input_cosmics__out1__-5GeV__v1_official"

#MYBIGQUERY="files from hd-protodune:hd-protodune__pdhd_mc_2025a__full-reconstructed__10_10_04d01__standard_reco_protodunehd_MC__pdhd_1GeV_h4input_cosmics__out1__-1GeV__v1_official"

MYBIGQUERY="files from hd-protodune:hd-protodune__pdhd_mc_2025a__full-reconstructed__10_10_04d01__standard_reco_protodunehd_MC__pdhd_5GeV_h4input_cosmics__out1__5GeV__v1_official"

#MYBIGQUERY="files from hd-protodune:hd-protodune__pdhd_mc_2025a__full-reconstructed__10_10_04d01__standard_reco_protodunehd_MC__pdhd_1GeV_h4input_cosmics__out1__1GeV__v1_official"




# -------------------------------
# Chunk configuration
# -------------------------------
CHUNK_SIZE=7000          # max files per workflow; default: 5000
CHUNK_INDEX=${1:-0}      # pass 0,1,2,... when running script
SKIP=$((CHUNK_INDEX * CHUNK_SIZE))

# Construct final MQL
MQL_QUERY="$MYBIGQUERY ordered skip ${SKIP} limit ${CHUNK_SIZE}"

echo "Submitting chunk ${CHUNK_INDEX}"
echo "MQL = $MQL_QUERY"


# ---------------------
# Job settings
# ---------------------
JOBSCRIPT="./michelMC_10sPerJob.jobscript"
FILES_PER_JOB=10


# ---------------------
# Output destination (WebDAV scratch)
# ---------------------
# IMPORTANT: Use HTTPS WebDAV door for dCache scratch, NOT /pnfs/...
# JustIN wrapper will upload matching outputs after your jobscript finishes. :contentReference[oaicite:2]{index=2}
WEBDAV_SCRATCH_DIR="https://fndcadoor.fnal.gov:2880/dune/scratch/users/szh2/MC_pdhd_Michel/official_2025Production/"


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
--output-pattern "mcTruth_*.txt:${WEBDAV_SCRATCH_DIR}" \
--lifetime-days 1 \
--classad 'DESIRED_Sites="US_FNAL-FermiGrid"'


#--env "NUM_EVENTS=3" \