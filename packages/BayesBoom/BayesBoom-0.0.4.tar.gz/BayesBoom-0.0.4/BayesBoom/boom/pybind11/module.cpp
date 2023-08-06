#include <pybind11/pybind11.h>
#include <pybind11/eigen.h>

#include <cpputil/Ptr.hpp>
namespace py = pybind11;
using namespace BOOM;
PYBIND11_DECLARE_HOLDER_TYPE(T, BOOM::Ptr<T>, true);

namespace BayesBoom {
  // Forward definitions of all the class definitions to be added in other
  // files.  Each of these is defined in a local cpp file, but invoked here.
  // That way all the definitions occur within the same module.
  void distribution_def(py::module &);
  void LinAlg_def(py::module &);
  void stats_def(py::module &);
  void Model_def(py::module &);
  void Data_def(py::module &);
  void Parameter_def(py::module &);
  void GaussianModel_def(py::module &);
  void GammaModel_def(py::module &);
  void MvnModel_def(py::module &);
  void GlmModel_def(py::module &);
  void Imputation_def(py::module &);
  void TimeSeries_def(py::module &);
  void StateSpaceModel_def(py::module &);
  void StateModel_def(py::module &);
  void DynamicRegressionModel_def(py::module &);

  PYBIND11_MODULE(_boom, boom) {
    boom.doc() = "BOOM stands for 'Bayesian Object Oriented Models'.  "
        "It is also the sound your computer makes when it crashes.\n\n"
        "BOOM is a C++ library written by Steven L. Scott.  It is a standalone "
        "C++ library, but also the engine behind a couple of useful R packages "
        "and (now) some python.\n\n"
        "The BayesBoom.boom package is intended for library writers and should "
        "probably not be used directly."
        ;

    // Calling these functions here defines the classes in the module.
    distribution_def(boom);
    LinAlg_def(boom);

    Data_def(boom);
    // stats includes DataTable, which inherits from Data.  Thus it must be
    // defined after Models, where the Data class is defined.

    stats_def(boom);

    Model_def(boom);
    Parameter_def(boom);
    GaussianModel_def(boom);
    GammaModel_def(boom);
    MvnModel_def(boom);

    GlmModel_def(boom);
    TimeSeries_def(boom);
    StateSpaceModel_def(boom);
    StateModel_def(boom);

    Imputation_def(boom);

    DynamicRegressionModel_def(boom);

  }  // Module BOOM

}  // namespace BayesBoom
