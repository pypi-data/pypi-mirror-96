
from .._network import Network
from .._population import Population
from .._outputfiles import OutputFiles
from .._workspace import Workspace

from ..utils._get_functions import call_function_on_network

__all__ = ["output_basic"]


def output_basic_serial(network: Network, population: Population,
                        output_dir: OutputFiles,
                        workspace: Workspace,
                        **kwargs):
    """This will write basic trajectory data to the output
       files. This will be the number of infected wards,
       total infections, play infections and work infections
       for each disease stage for each timestep

       Parameters
       ----------
       network: Network
         The network over which the outbreak is being modelled
       population: Population
         The population experiencing the outbreak
       output_dir: OutputFiles
         The directory in which to place all output files
       workspace: Workspace
         A workspace that can be used to extract data
       kwargs
         Extra argumentst that are ignored by this function
    """

    if network.name is None:
        name = ""
    else:
        name = "_" + network.name.replace(" ", "_")

    def get_headers(FILE):
        disease = network.params.disease_params
        FILE.write("day," + ",".join(disease.stage) + "\n")

    # get the file handles - this will open the files if
    # they have not already been created
    n_inf_wards_file = output_dir.open(f"number_infected_wards{name}.csv",
                                       headers=get_headers)
    total_file = output_dir.open(f"total_infections{name}.csv",
                                 headers=get_headers)
    work_file = output_dir.open(f"work_infections{name}.csv",
                                headers=get_headers)
    play_file = output_dir.open(f"play_infections{name}.csv",
                                headers=get_headers)

    ts = f"{population.day},"

    def _join(array):
        return ",".join([str(x) for x in array])

    total = [inf + pinf for inf, pinf in zip(workspace.inf_tot,
                                             workspace.pinf_tot)]

    total_file.write(ts + _join(total) + "\n")
    n_inf_wards_file.write(ts + _join(workspace.n_inf_wards) + "\n")
    work_file.write(ts + _join(workspace.inf_tot) + "\n")
    play_file.write(ts + _join(workspace.pinf_tot) + "\n")


def output_basic(nthreads: int = 1, **kwargs):
    """This will write basic trajectory data to the output
       files. This will be the number of infected wards,
       total infections, play infections and work infections
       for each disease stage for each timestep

       Parameters
       ----------
       network: Network
         The network over which the outbreak is being modelled
       population: Population
         The population experiencing the outbreak
       output_dir: OutputFiles
         The directory in which to place all output files
       workspace: Workspace
         A workspace that can be used to extract data
       kwargs
         Extra argumentst that are ignored by this function
    """
    call_function_on_network(nthreads=1,
                             func=output_basic_serial,
                             call_on_overall=True,
                             **kwargs)
