////////////////////////////////////////////////////////////////////////
// Class:       Truechecks
// Plugin Type: analyzer
// File:        Truechecks_module.cc
//
// Generated at Tue Feb 4 15:23:48 2025 by Jeremy Quelin Lechevranton
////////////////////////////////////////////////////////////////////////

// Art includes
#include "art/Framework/Core/EDAnalyzer.h"
#include "art/Framework/Core/ModuleMacros.h"
#include "art/Framework/Principal/Event.h"
#include "art/Framework/Principal/Handle.h"
#include "art/Framework/Principal/Run.h"
#include "art/Framework/Principal/SubRun.h"
#include "canvas/Utilities/InputTag.h"
#include "fhiclcpp/ParameterSet.h"
#include "messagefacility/MessageLogger/MessageLogger.h"
#include "canvas/Persistency/Common/FindManyP.h"
#include "art_root_io/TFileService.h"

// LArSoft includes
#include "larsim/MCCheater/ParticleInventoryService.h"
#include "larsim/MCCheater/BackTrackerService.h"

#include "nusimdata/SimulationBase/MCTruth.h"
#include "nusimdata/SimulationBase/MCParticle.h"
#include "lardataobj/Simulation/SimEnergyDeposit.h"

#include "lardataobj/RecoBase/Hit.h"
#include "lardataobj/RecoBase/Wire.h"
#include "lardataobj/RecoBase/Track.h"
#include "lardataobj/RecoBase/SpacePoint.h"

#include "larcore/Geometry/Geometry.h"
#include "larcore/Geometry/WireReadout.h"

#include "larcorealg/Geometry/Exceptions.h"

#include "lardata/DetectorInfoServices/DetectorPropertiesService.h"
// #include "lardata/ArtDataHelper/TrackUtils.h"

// ProtoDUNE includes
#include "protoduneana/Utilities/ProtoDUNETrackUtils.h"
#include "protoduneana/Utilities/ProtoDUNETruthUtils.h"
#include "protoduneana/Utilities/ProtoDUNEPFParticleUtils.h"

// ROOT includes
#include "TLorentzVector.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TH3F.h"
#include "TLine.h"
#include "TGraph.h"
#include "TGraph2D.h"
#include "TEllipse.h"


// #include "ROOT/RVec.hxx"
// #include "RVec.hxx"

// std includes
#include <iostream>
#include <sstream>
#include <vector>
#include <string>
#include <iterator>
#include <map>
#include <unordered_map>
#include <numeric>
#include <algorithm>
#include <utility>

namespace ana {
    class Truechecks;
    struct Binning {
        int n;
        float min, max;
    };
}

class ana::Truechecks : public art::EDAnalyzer {
public:
    explicit Truechecks(fhicl::ParameterSet const& p);
    // The compiler-generated destructor is fine for non-base
    // classes without bare pointers or other resource use.

    // Plugins should not be copied or assigned.
    Truechecks(Truechecks const&) = delete;
    Truechecks(Truechecks&&) = delete;
    Truechecks& operator=(Truechecks const&) = delete;
    Truechecks& operator=(Truechecks&&) = delete;

    // Required functions.
    void analyze(art::Event const& e) override;

    // Selected optional functions.
    void beginJob() override;
    void endJob() override;

private:

    // Utilities
    art::ServiceHandle<art::TFileService> tfs;

    const geo::GeometryCore* asGeo;
    const geo::WireReadoutGeom* asWire;
    const detinfo::DetectorPropertiesService* asDetProp;
    const detinfo::DetectorClocksService* asDetClocks;

    protoana::ProtoDUNETruthUtils truthUtil;
    art::ServiceHandle<cheat::ParticleInventoryService> pi_serv;
    art::ServiceHandle<cheat::BackTrackerService> bt_serv;

    // Conversion factors
    float feltoMeV = 23.6 * 1e-6 / 0.7; // 23.6 eV/e- * 1e-6 MeV/eV / 0.7 recombination factor
    float fADCtoMeV = 200 * 23.6 * 1e-6 / 0.7; // 200 e-/ADC.tick * 23.6 eV/e- * 1e-6 MeV/eV / 0.7 recombination factor
    float fChannelPitch;
    float fDriftVelocity; // cm/µs
    float fSamplingRate; // µs/tick




    // Verbosity
    int iLogLevel;
    enum EnumFlag { kImportant, kBasics, kInfos, kDetails };


    // Diagnostic Variables
    std::map<std::string, unsigned> map_mup_endproc;
    std::map<std::string, unsigned> map_mum_endproc;
    unsigned n_mup=0, n_mum=0, n_mep=0, n_mem=0;
    unsigned n_cme_wh=0, n_cme_nh=0;
    float mean_cme_h=0;


    // Products
    std::vector<std::vector<std::string>> vvsProducts;
    art::InputTag   tag_mcp,
                    tag_sed,
                    tag_wir,
                    tag_hit,
                    tag_clu,
                    tag_trk,
                    tag_spt;

    bool Log(bool cond, int flag, int tab, std::string msg, std::string succ, std::string fail);
    std::string GetParticleName(int pdg);
};





ana::Truechecks::Truechecks(fhicl::ParameterSet const& p)
    : EDAnalyzer{p},
    iLogLevel(p.get<int>("LogLevel")),
    vvsProducts(p.get<std::vector<std::vector<std::string>>>("Products"))
{
    if (iLogLevel >= kBasics) 
        std::cout << "\n\n\033[93m" << "Truechecks::Truechecks: =================" << "\033[0m" << std::endl;
    // Basic Utilities
    asGeo = &*art::ServiceHandle<geo::Geometry>();
    asWire = &art::ServiceHandle<geo::WireReadout>()->Get();
    asDetProp = &*art::ServiceHandle<detinfo::DetectorPropertiesService>();    
    asDetClocks = &*art::ServiceHandle<detinfo::DetectorClocksService>();

    geo::WireGeo const wiregeo1 = asWire->Wire(geo::WireID{geo::PlaneID{geo::TPCID{0, 0}, geo::kW}, 0});
    geo::WireGeo const wiregeo2 = asWire->Wire(geo::WireID{geo::PlaneID{geo::TPCID{0, 0}, geo::kW}, 1});
    fChannelPitch = geo::WireGeo::WirePitch(wiregeo1, wiregeo2);

    auto const clockData = asDetClocks->DataForJob();
    auto const detProp = asDetProp->DataForJob(clockData);

    // Retrieving product tags
    for (std::vector<std::string> prod : vvsProducts) {

        const std::string   process     = prod[0],
                            label       = prod[1],
                            instance    = prod[2],
                            type        = prod[3];

        const art::InputTag tag = art::InputTag(label,instance);

        if      (type == "simb::MCParticle")        tag_mcp = tag;
        else if (type == "sim::SimEnergyDeposit")   tag_sed = tag;
        else if (type == "recob::Hit")              tag_hit = tag;
        else if (type == "recob::Wire")             tag_wir = tag;
        else if (type == "recob::Cluster")          tag_clu = tag;
        else if (type == "recob::Track")            tag_trk = tag;
        else if (type == "recob::SpacePoint")       tag_spt = tag;
    }

    // fSamplingRate = detinfo::sampling_rate(clockData) * 1e-3;
    // fDriftVelocity = detProp.DriftVelocity();

    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "End of Truechecks::Truechecks ==========" << "\033[0m\n" << std::endl;
}








void ana::Truechecks::analyze(art::Event const& e)
{

    if (iLogLevel >= kBasics) {
        std::cout << "\n\n\n\033[93m" << "Truechecks::analyze: Initialization evt#" << std::setw(5) << e.id().event() << " ====================================" << "\033[0m" << std::endl;
    }

    auto const clockData = asDetClocks->DataFor(e);
    auto const detProp = asDetProp->DataFor(e,clockData);
    fSamplingRate = detinfo::sampling_rate(clockData) * 1e-3;
    fDriftVelocity = detProp.DriftVelocity();

    auto const & vh_trk = e.getValidHandle<std::vector<recob::Track>>(tag_trk);
    std::vector<art::Ptr<recob::Track>> vp_trk;
    art::fill_ptr_vector(vp_trk, vh_trk);

    std::vector<unsigned> n_dau;
    std::vector<unsigned> n_muioni;
    std::vector<std::vector<int>> dau_pdg;
    std::vector<std::vector<std::string>> dau_process;


    if (iLogLevel >= kInfos) std::cout << "LOOPING over " << vp_trk.size() << " tracks..." << std::endl;

    //Shu: Track-level processing, 20250703---
    for (art::Ptr<recob::Track> const& p_trk : vp_trk) {
        if (iLogLevel >= kInfos) std::cout << "trk#" << p_trk->ID() << "\r" << std::flush;

        if (p_trk->Length() < 40) continue; //Shu: remove short tracks (expect muon long enough), 20250703---

        // Print reco track's reconstructed endpoint
        std::cout << "\tMuonRecoEnd ("
                  << p_trk->End().X() << ", "
                  << p_trk->End().Y() << ", "
                  << p_trk->End().Z() << ") " << std::endl;





        //Shu: The key, all info of track particle can be acquired here, 20250703---
        //Shu: (ChatGPT) For a certain Pandora reco track, find the most likely MC truth particle---
        //Shu: This method is convenient, but not always accurate, especially in dense or noisy events. 
        //It only gives the MCParticle that contributed the most charge via BackTrackerService, 
        //not necessarily the one that aligns best in 3D
        //        simb::MCParticle const * mcp = truthUtil.GetMCParticleFromRecoTrack(clockData, *p_trk, e, tag_trk.label());

        //MCPartcile finding for current reco track-------------------------------------------------------
        // Step 1: Try truthUtil match first
        simb::MCParticle const* mcp = truthUtil.GetMCParticleFromRecoTrack(clockData, *p_trk, e, tag_trk.label());

        bool use_fallback = false;
        double dist_truthutil = 9999.0;

        if (mcp && std::abs(mcp->PdgCode()) == 13 && mcp->EndProcess() != "Transportation") {
            double dx = p_trk->End().X() - mcp->EndX();
            double dy = p_trk->End().Y() - mcp->EndY();
            double dz = p_trk->End().Z() - mcp->EndZ();
            dist_truthutil = std::sqrt(dx * dx + dy * dy + dz * dz);
            if (dist_truthutil > 15.0) 
                use_fallback = true;
        } 
        else {
            use_fallback = true;
        }


        // Step 2: Fallback — match by closest muon decay point with IDE energy threshold
        // Compute energy_by_trackid earlier in the loop
        // Get hits associated with current reco track p_trk
        auto const& vh_trk = e.getValidHandle<std::vector<recob::Track>>(tag_trk);
        art::FindManyP<recob::Hit> trackToHits(vh_trk, e, tag_trk.label());

        std::vector<const recob::Hit*> track_hits;
        if (trackToHits.isValid() && trackToHits.at(p_trk.key()).size()) {
            for (const auto& hit_ptr : trackToHits.at(p_trk.key())) {
                track_hits.push_back(hit_ptr.get());
            }
        }

        // Accumulate IDE energy per MCParticle that contributed to those hits
        std::map<int, double> energy_by_trackid;
        for (const recob::Hit* hit : track_hits) {
            std::vector<sim::TrackIDE> ides = bt_serv->HitToTrackIDEs(clockData, *hit);
            for (const auto& ide : ides) {
                energy_by_trackid[ide.trackID] += ide.energy; // unit: MeV
            }
        }

        if (use_fallback) {
            std::cout << "\t[Matching Fallback]" << std::endl;

            auto const& mcp_handle = e.getValidHandle<std::vector<simb::MCParticle>>(tag_mcp);
            double min_dist = std::numeric_limits<double>::max();
            simb::MCParticle const* best_mcp = nullptr;

            for (auto const& mcp_cand : *mcp_handle) {
                if (std::abs(mcp_cand.PdgCode()) != 13) continue;
                if (mcp_cand.EndProcess() == "Transportation") continue;

                int trackID = mcp_cand.TrackId();

                // Require this particle contributed significant IDE energy to reco hits
                auto it = energy_by_trackid.find(trackID);
                if (it == energy_by_trackid.end()) continue;
                if (it->second < 0.5) continue; // IDE energy threshold

                double dx = p_trk->End().X() - mcp_cand.EndX();
                double dy = p_trk->End().Y() - mcp_cand.EndY();
                double dz = p_trk->End().Z() - mcp_cand.EndZ();
                double dist = std::sqrt(dx * dx + dy * dy + dz * dz);

                if (dist < min_dist) {
                    min_dist = dist;
                    best_mcp = &mcp_cand;
                }
            }

            // Add debug logging before decision
            std::cout << "\t[Matching Fallback] min_dist = " << min_dist << std::endl;


            if (best_mcp && min_dist < 15.0) {
                mcp = best_mcp;
                std::cout << "\t[Matching Fallback] Match accepted" << std::endl;
            }
            else {
                std::cout << "\t[Matching Fallback] No valid match " << std::endl;
                mcp = nullptr;
            }
            
        }


        // Step 3: Reject if no usable match
        if (!mcp) {
                std::cout << "\tNo usable MC match." << std::endl;
                continue;
        }
        //------------------------------------------------------------------------------------------------











        if (!mcp) continue; //Shu: No match, jump; 20250703---
        if (abs(mcp->PdgCode()) != 13) continue; //Shu: If the track is not mu^- / mu^+, jump; 20250703---


        if (mcp->EndProcess() == "Transportation") continue; //Shu: through-going muons, jump; 20250703---

        if (mcp->PdgCode() > 0) { //Shu: count mu^-; 20250703---
            n_mum++;
            map_mum_endproc[mcp->EndProcess()]++;
        } else {
            n_mup++;
            map_mup_endproc[mcp->EndProcess()]++;
        }

        unsigned tp_n_dau=0;
        unsigned tp_n_muioni=0;
        std::vector<int> tp_dau_pdg;
        std::vector<std::string> tp_dau_process;
        for (int i_dau=0; i_dau<mcp->NumberDaughters(); i_dau++) { //Shu: loop over mu's daughter particles, 20250703---
            simb::MCParticle const * mcp_dau = pi_serv->TrackIdToParticle_P(mcp->Daughter(i_dau));
            if (!mcp_dau) continue; //Shu: No daughter particle; jump; 20250703---

            tp_n_dau++;

            if (mcp_dau->Process() == "muIoni" && mcp_dau->PdgCode() == 11) {
                tp_n_muioni++;
                continue;
            }

            tp_dau_pdg.push_back(mcp_dau->PdgCode());
            tp_dau_process.push_back(mcp_dau->Process());
        }
        n_dau.push_back(tp_n_dau);
        n_muioni.push_back(tp_n_muioni);
        dau_pdg.push_back(tp_dau_pdg);
        dau_process.push_back(tp_dau_process);
    
        if (mcp->NumberDaughters() < 3) continue; //Shu: For real decay of muon, at least 3 daughter particles, 20250703---

        bool has_numu=false, has_nue=false;
        simb::MCParticle const * mcp_mich = nullptr;
        for (int i_dau=mcp->NumberDaughters()-3; i_dau<mcp->NumberDaughters(); i_dau++) {
            simb::MCParticle const * mcp_dau = pi_serv->TrackIdToParticle_P(mcp->Daughter(i_dau));
            if (!mcp_dau) continue;
            switch (abs(mcp_dau->PdgCode())) {
                case 14: has_numu = true; break;
                case 12: has_nue = true; break;
                case 11: mcp_mich = mcp_dau; break;
                default: break;
            }
        }

        if (!(has_nue and has_numu and mcp_mich)) continue;

        if (mcp->PdgCode() > 0) n_mem++; //Shu: # of decayed mu^-, 20250703---
        else n_mep++;

        std::vector<const recob::Hit*> v_hit_michel = truthUtil.GetMCParticleHits(clockData, *mcp_mich, e, tag_hit.label());
        if (mcp->EndProcess() == "muMinusCaptureAtRest") {
            if (v_hit_michel.size()) {
                n_cme_wh++;
                mean_cme_h += v_hit_michel.size();
            } else {
                n_cme_nh++;
            }
        }


        std::cout << "\t[Michel observed!] (" << GetParticleName(mcp_mich->PdgCode()) << ") / mcp::TrackID: " <<  mcp_mich->TrackId() << " / " << v_hit_michel.size() << " hits" << std::endl;
        //Modified by Shu, 20250703---
        std::cout << "\tMichel True K-energy : " << (mcp_mich->E() - mcp_mich->Mass()) * 1e3 << " MeV" << std::endl;
        std::cout << "\tMichel origin position: (x, y, z, t)[cm, ns]   = (" << mcp_mich->Vx() << ", " << mcp_mich->Vy() << ", " << mcp_mich->Vz() << ", " << mcp_mich->T() << ")" << std::endl;
        std::cout << "\tMCTruth muon stops at (x1, y1, z1, t1)[cm, ns] = (" << mcp->EndX() << ", " << mcp->EndY() << ", " << mcp->EndZ() << ", " << mcp->EndT() << ")" << std::endl;
        std::cout << "\tMCTruth muon starts at (x0, y0, z0, t0)[cm, ns]= (" << mcp->Vx() << ", " << mcp->Vy() << ", " << mcp->Vz() << ", " << mcp->T() << ")" << std::endl;
        std::cout << "\tMCTruth muon lifetime [us]: " << (mcp->EndT() - mcp->T()) * 1e-3 << std::endl;  
        
        




        float mich_ide_energy = 0;
        float mich_hit_energy = 0;

//        unsigned i_hit=0;
        for (const recob::Hit* hit_michel : v_hit_michel) {
            if (hit_michel->View() != geo::kW) continue;

            mich_hit_energy += hit_michel->Integral() * fADCtoMeV;

            std::vector<sim::TrackIDE> v_tid = bt_serv->HitToTrackIDEs(clockData, *hit_michel); 
//            std::cout << "\thit#" << i_hit++
//                << " Integral: " << hit_michel->Integral() * fADCtoMeV
//                << " MeV  / ROIADC: " << hit_michel->ROISummedADC() * fADCtoMeV
//                << " MeV / "  << v_tid.size() << " trackIDEs"
//                << std::endl;

//            unsigned i_tid=0;
            for (const sim::TrackIDE& tid : v_tid) {
//                simb::MCParticle const * mcp_tid = pi_serv->TrackIdToParticle_P(tid.trackID);
                // std::cout << "\t\t\ttIDE#" << i_tid++
                //     << " trackID: " << (tid.trackID == mcp_mich->TrackId() ? "\033[92m" : "\033[91m") << tid.trackID << "\033[0m"
                //     << " (" << GetParticleName(mcp_tid->PdgCode()) << ")"
                //     << " energy: " << tid.energy
                //     << " energyFrac: " << tid.energyFrac
                //     << " numElectrons: " << tid.numElectrons
                //     << " (" << tid.numElectrons * feltoMeV << " MeV)"
                //     << std::endl;
                if (tid.trackID == mcp_mich->TrackId()) {
                   mich_ide_energy += tid.energy; 
                }
            }
        }

//        std::cout << "\tMichel IDE energy: " << mich_ide_energy << " MeV"
//            << " / Michel Hit energy: " << mich_hit_energy << " MeV"
//            << std::endl;
    }



    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "End of Truechecks::analyze =======================================================" << "\033[0m" << std::endl;
} // end analyze

void ana::Truechecks::beginJob()
{
    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "Truechecks::beginJob: ============================================================" << "\033[0m" << std::endl;
    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "End of Truechecks::beginJob ======================================================" << "\033[0m" << std::endl;
} // end beginJob


void ana::Truechecks::endJob()
{
    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "Truechecks::endJob: ==============================================================" << "\033[0m" << std::endl;

    std::cout << "µ+ decay rate: " << 100.*n_mep / n_mup << "% (" << n_mup << ")" << std::endl;
    for (auto const& [key, val] : map_mup_endproc) {
        std::cout << "  " << key << ": " << val << std::endl;
    }
    std::cout << "µ- decay rate: " << 100.*n_mem / n_mum << "% (" << n_mum << ")" << std::endl;
    for (auto const& [key, val] : map_mum_endproc) {
        std::cout << "  " << key << ": " << val << std::endl;
    }
    std::cout << "µ- decaying after capture: " << 100.*(n_cme_wh + n_cme_nh) / map_mum_endproc["muMinusCaptureAtRest"] << "% (" << (n_cme_wh + n_cme_nh) << ")" << std::endl;
    std::cout << "  w/ hits: " << n_cme_wh << " (~" << mean_cme_h/n_cme_wh << " hits/michel)" << std::endl;
    std::cout << "  w/o hit: " << n_cme_nh << std::endl;


    if (iLogLevel >= kBasics) std::cout << "\033[93m" << "End of Truechecks::endJob ========================================================" << "\033[0m\n\n" << std::endl;
} // end endJob




bool ana::Truechecks::Log(bool cond, int flag, int tab, std::string msg, std::string succ, std::string fail) {
    if (iLogLevel >= flag) {
        std::cout << std::string(tab,'\t') << msg << " ";
        if (cond) std::cout << "\033[92m" << succ << "\033[0m" << std::endl;
        else std::cout << "\033[91m" << fail << "\033[0m" << std::endl;
    }
    return cond;
}

std::string ana::Truechecks::GetParticleName(int pdg) {

    std::vector<std::string> periodic_table = { "",
        "H",                                                                                                  "He", 
        "Li", "Be",                                                             "B",  "C",  "N",  "O",  "F",  "Ne",
        "Na", "Mg",                                                             "Al", "Si", "P",  "S",  "Cl", "Ar",
        "K",  "Ca", "Sc", "Ti", "V",  "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
        "Rb", "Sr", "Y",  "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn", "Sb", "Te", "I",  "Xe"
    };

    switch (pdg) {
        case 11: return "e-";
        case -11: return "e+";
        case 12: return "ve";
        case -12: return "-ve";
        case 13: return "µ-";
        case -13: return "µ+";
        case 14: return "vµ";
        case -14: return "-vµ";
        case 22: return "γ";
        case 2212: return "p";
        case 2112: return "n";
    }

    if (pdg > 1000000000) {
        unsigned ex = pdg % 10;
        unsigned A = (pdg / 10) % 1000;
        unsigned Z = (pdg / 10000) % 1000;
        unsigned L = (pdg / 10000000);
        if (L==100 && Z && Z < periodic_table.size()) return Form("%u%s%s", A, periodic_table[Z].c_str(), ex ? "*" : "");
    }

    return Form("%d", pdg);
}

DEFINE_ART_MODULE(ana::Truechecks)
