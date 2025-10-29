#Shu: change RUN_ID each time, 20250808---
#RUN_ID here is used to count event number

jobsub_submit -G dune \
  --mail_never \
  -N 10000 \
  --memory=20000MB \
  --disk=25GB \
  --cpu=1 \
  --expected-lifetime=8h \
  --tar_file_name=dropbox:///exp/dune/app/users/szh2/michel_Jul2025/michel20251001.tar.gz \
  --resource-provides=usage_model=DEDICATED,OPPORTUNISTIC,OFFSITE \
  --singularity-image /cvmfs/singularity.opensciencegrid.org/fermilab/fnal-wn-sl7:latest \
  --append_condor_requirements='(TARGET.HAS_Singularity==true && TARGET.HAS_CVMFS_dune_opensciencegrid_org==true && TARGET.HAS_CVMFS_larsoft_opensciencegrid_org==true && TARGET.CVMFS_dune_opensciencegrid_org_REVISION>=1105)' \
  -e GFAL_PLUGIN_DIR=/usr/lib64/gfal2-plugins \
  -e GFAL_CONFIG_DIR=/etc/gfal2.d \
  -e RUN_ID=42 \
  file:///exp/dune/app/users/szh2/michel_Jul2025/work/my_pdhd_production/run_all.sh

