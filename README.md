# analyze_pdhd_DATA_v2
Michel electron analysis of both DATA and MC

## statScript:
Mainly doing TPC solely processing. 
Including Space cut, MS cut and MH cut



## analyze:
    Waveform related processing:
    Waveform coincidence, peakFinder & coincidence


    ### coreScript_v1:
        The core script of previous analysis (single processing)


    ### v2_main:
        The current MOST IMPORTANT folder, large-quantity processing;
        full28867 analyzed; basis of DUNE CM May 2025


    ### v2_rawDecon_misMatch_explore:
        To explore the channel number discrepancy between raw and deconv data
        Finally found that opch35 is missing (finally recovered by working group)


    ### viktor_deconv_explore:
        suggested by Viktor
        To explore effects of different settings (test filter)
