//=============================================================
// KillMuonsOutsideBox tool — removes through-going muons
// Compatible with artg4tk v10_05_03 + larsoft v10_12_02
// Created by Shuaixiang (Shu) Zhang
//=============================================================

#include "fhiclcpp/types/Atom.h"
#include "fhiclcpp/types/Sequence.h"
#include "fhiclcpp/types/TableFragment.h"
#include "fhiclcpp/ParameterSet.h"
#include "art/Utilities/ToolMacros.h"
#include "artg4tk/actionBase/SteppingActionBase.hh"

#include "G4Step.hh"
#include "G4Track.hh"
#include "G4SystemOfUnits.hh"

#include <vector>
#include <algorithm>


namespace larg4tools {

  class KillMuonsOutsideBox : public artg4tk::SteppingActionBase {
  public:
    struct Config {
      fhicl::Sequence<int> PDGs{ fhicl::Name("PDGs"),
                                 fhicl::Comment("PDGs to act on"),
                                 std::vector<int>{13, -13} };

      fhicl::Sequence<double> BoundsX{ fhicl::Name("BoundsX"),
                                       fhicl::Comment("[xmin,xmax] in cm") };
      fhicl::Sequence<double> BoundsY{ fhicl::Name("BoundsY"),
                                       fhicl::Comment("[ymin,ymax] in cm") };
      fhicl::Sequence<double> BoundsZ{ fhicl::Name("BoundsZ"),
                                       fhicl::Comment("[zmin,zmax] in cm") };

      fhicl::Atom<double> EdgeTolerance{ fhicl::Name("EdgeTolerance"),
                                         fhicl::Comment("Tolerance in cm"),
                                         0.05 };

      fhicl::Atom<double> MaxMuonEnergy{ fhicl::Name("MaxMuonEnergy"),
                                         fhicl::Comment("Kill muons above this KE (in GeV). Default = no cut."),
                                         1.0e9 }; // effectively infinite
    };

    using Parameters = fhicl::TableFragment<Config>;

    // --- Modern constructor ---
    explicit KillMuonsOutsideBox(Parameters const& p)
      : artg4tk::SteppingActionBase("KillMuonsOutsideBox"),
        pdgs_{p().PDGs()},
        xmin_{p().BoundsX()[0]}, xmax_{p().BoundsX()[1]},
        ymin_{p().BoundsY()[0]}, ymax_{p().BoundsY()[1]},
        zmin_{p().BoundsZ()[0]}, zmax_{p().BoundsZ()[1]},
        tol_{p().EdgeTolerance()},
        maxE_{p().MaxMuonEnergy() * GeV}   // convert GeV → MeV
    {}

    // --- Legacy constructor (for older artg4tk builds) ---
    explicit KillMuonsOutsideBox(fhicl::ParameterSet const& p)
      : artg4tk::SteppingActionBase("KillMuonsOutsideBox"),
        pdgs_{p.get<std::vector<int>>("PDGs", {13, -13})},
        xmin_{p.get<std::vector<double>>("BoundsX").at(0)},
        xmax_{p.get<std::vector<double>>("BoundsX").at(1)},
        ymin_{p.get<std::vector<double>>("BoundsY").at(0)},
        ymax_{p.get<std::vector<double>>("BoundsY").at(1)},
        zmin_{p.get<std::vector<double>>("BoundsZ").at(0)},
        zmax_{p.get<std::vector<double>>("BoundsZ").at(1)},
        tol_{p.get<double>("EdgeTolerance", 0.05)},
        maxE_{p.get<double>("MaxMuonEnergy", 1.0e9) * GeV}
    {}

    // --- Main stepping action ---
    void userSteppingAction(const G4Step* step) override {
      auto* track = step->GetTrack();
      if (!track) return;

      int pdg = track->GetDefinition()->GetPDGEncoding();
      if (std::find(pdgs_.begin(), pdgs_.end(), pdg) == pdgs_.end()) return;

      // ---  Energy cut ---
      double KE = track->GetKineticEnergy(); // MeV
      if (KE > maxE_) {
        track->SetTrackStatus(fStopAndKill);
        return;
      }

      // ---  Inside/outside volume test ---
      auto const pre  = step->GetPreStepPoint()->GetPosition();
      auto const post = step->GetPostStepPoint()->GetPosition();

      bool in  = inside(pre.x()/cm,  pre.y()/cm,  pre.z()/cm);
      bool out = inside(post.x()/cm, post.y()/cm, post.z()/cm);

      if (!in && !out)  { track->SetTrackStatus(fStopAndKill); return; }
      if (in && !out)   { track->SetTrackStatus(fStopAndKill); return; }
    }

  private:
    std::vector<int> pdgs_;
    double xmin_, xmax_, ymin_, ymax_, zmin_, zmax_, tol_;
    double maxE_;   // Max muon energy in MeV

    inline bool inside(double x, double y, double z) const {
      return (x > xmin_ - tol_ && x < xmax_ + tol_ &&
              y > ymin_ - tol_ && y < ymax_ + tol_ &&
              z > zmin_ - tol_ && z < zmax_ + tol_);
    }
  };

} // namespace larg4tools

DEFINE_ART_CLASS_TOOL(larg4tools::KillMuonsOutsideBox);