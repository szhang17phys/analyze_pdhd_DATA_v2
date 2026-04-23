MQL_QUERY="files from justin-tutorial:justin-tutorial-2024 limit 10"

justin simple-workflow \
--mql "$MQL_QUERY" \
--jobscript-git \
   DUNE/dune-justin/testing/dc4-vd-coldbox-bottom.jobscript:01.00.00 \
--max-distance 9999 \
--rss-mib 4000 --env NUM_EVENTS=1 --scope usertests \
--output-pattern '*_reco_data_*.root:output-test' \
--lifetime-days 1