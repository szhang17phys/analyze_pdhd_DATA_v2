find_package(artg4tk REQUIRED)
include_directories($ENV{ARTG4TK_DIR}/include)

# Add Geant4 includes (for G4Step.hh, G4Track.hh, etc.)
include_directories(/cvmfs/larsoft.opensciencegrid.org/products/geant4/v4_10_6_p01g/Linux64bit+3.10-2.17-e26-prof/include/Geant4)
link_directories($ENV{ARTG4TK_DIR}/slf7.x86_64.e26.prof/lib)


art_make(BASENAME_ONLY
    TOOL_LIBRARIES
        artg4tk_actionBase
        art::Framework_Core
        art::Framework_Principal
        art::Framework_Services_Registry
        art::Persistency_Common
        canvas::canvas
        messagefacility::MF_MessageLogger
        cetlib::cetlib
        cetlib_except::cetlib_except
        larcorealg::Geometry
        lardataalg::DetectorInfo
        nusimdata::SimulationBase
        ROOT::Core ROOT::Tree ROOT::Hist
)

install_headers()
install_fhicl()
install_source()
