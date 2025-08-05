#!/bin/bash

USERF=$USER
FNALURL='https://fndcadoor.fnal.gov:2880/dune/scratch/users'
DEST="$FNALURL/$USERF/MC_pdhd_Michel/MY_production"

# justin simple-workflow \
#   --monte-carlo 3 \
#   --jobscript simuHD.jobscript \
#   --output-pattern "cosmic_g4_stage2_*.root:$DEST" \
#   --output-rse FNAL_DCACHE_USER \
#   --scope usertests \
#   --lifetime-days 1


justin simple-workflow \
  --monte-carlo 3 \
  --jobscript simuHD.jobscript \
  --output-pattern "cosmic_g4_*.root:$DEST" \
  --output-rse FNAL_DCACHE_USER \
  --scope usertests \
  --lifetime-days 1