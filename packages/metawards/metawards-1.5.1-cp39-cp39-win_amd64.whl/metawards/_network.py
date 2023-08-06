
from dataclasses import dataclass as _dataclass
from typing import List as _List
from typing import Union as _Union
from typing import Tuple as _Tuple

from enum import Enum as _Enum

from ._parameters import Parameters
from ._disease import Disease
from ._nodes import Nodes
from ._links import Links
from ._population import Population
from ._outputfiles import OutputFiles
from ._wardinfo import WardInfos
from ._wardid import WardID

__all__ = ["Network", "PersonType"]


class PersonType(_Enum):
    """The type of individual in the network."""
    #: A WORKER is an individual that makes fixed movements between
    #: their home and commute (work) ward
    WORKER = 1
    #: A PLAYER is an individual who makes random movements between
    #: their home ward and the play wards linked to their home ward
    PLAYER = 2

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return self.value == other.value
        else:
            return self.name == other or self.value == other


@_dataclass
class Network:
    """This class represents a network of wards. The network comprises
       nodes (representing wards), connected with links which represent
       work (predictable movements) and play (unpredictable movements)
    """
    #: The name of the Network. This equals the name of the demographic
    #: if this is a multi-demographic sub-network
    name: str = None

    #: The list of nodes (wards) in the network
    nodes: Nodes = None
    #: The links between nodes (work)
    links: Links = None
    #: The links between nodes (play)
    play: Links = None

    #: The number of nodes in the network
    nnodes: int = 0
    #: The number of links in the network
    nlinks: int = 0
    #: The number of play links in the network
    nplay: int = 0

    #: The maximum allowable number of nodes in the network
    max_nodes: int = 16384
    #: The maximum allowable number of links in the network
    max_links: int = 4194304

    #: The metadata for all of the wards
    info: WardInfos = WardInfos()

    #: To seed provides additional seeding information
    to_seed: _List[int] = None

    #: The parameters used to generate this network
    params: Parameters = None

    #: The number of workers
    work_population: int = None

    #: The number of players
    play_population: int = None

    #: The index in the overall network's work matrix of the ith
    #: index in this subnetworks work matrix. If this is None then
    #: both this subnetwork has the same work matrix as the overall
    #: network
    _work_index = None

    @property
    def population(self) -> int:
        """Return the total population in the network"""
        if self.nodes is None:
            return 0

        node_pop = self.nodes.population()
        link_pop = self.links.population()

        return int(node_pop + link_pop)

    @staticmethod
    def single(params: Parameters,
               population: Population,
               profiler=None):
        """Builds and returns a new Network that contains just a single
           ward, in which 'population' individuals are resident.
        """
        if profiler is None:
            from .utils import NullProfiler
            profiler = NullProfiler()

        pop = float(population.population)

        if pop <= 0:
            pop = float(population.initial)

        if pop <= 0:
            raise ValueError(
                f"You cannot create a Network with a zero or negative "
                f"population ({population}).")

        from .utils._console import Console
        Console.print(
            f"Creating a single ward Network with a population "
            f"of {int(pop)}")

        from ._wards import Wards
        from ._ward import Ward

        ward = Ward(name="single")
        ward.set_num_players(pop)

        wards = Wards()
        wards.add(ward)

        assert wards.population() == pop

        network = Network.from_wards(wards, params=params)
        network.params.input_files = params.input_files

        return network

    @staticmethod
    def build(params: Parameters,
              population: Population = None,
              max_nodes: int = 16384,
              max_links: int = 4194304,
              nthreads: int = 1,
              profiler=None):
        """Builds and returns a new Network that is described by the
           passed parameters.

           The network is built in allocated memory, so you need to specify
           the maximum possible number of nodes and links. The memory buffers
           will be shrunk back after building.
        """
        if profiler is None:
            from .utils import NullProfiler
            profiler = NullProfiler()

        p = profiler.start("Network.build")

        if params.input_files is None:
            from .utils._console import Console
            Console.error("You must specify the model/network to use, e.g. "
                          "setting it from 'single', from a Wards object, "
                          "or specifying the model to load from "
                          "MetaWardsData")
            raise AssertionError("You must specify the model to run")
        elif params.input_files.is_wards_data:
            from ._wards import Wards
            wards = Wards.from_json(params.input_files.wards_data)
            network = Network.from_wards(wards, params=params,
                                         profiler=p, nthreads=nthreads)
            network.params.input_files = params.input_files

            p.stop()
            return network

        elif params.input_files.is_single:
            if population is None:
                population = Population(initial=1000)

            network = Network.single(params=params,
                                     population=population,
                                     profiler=profiler)
            p.stop()
            return network

        p = p.start("build_function")
        from .utils import build_wards_network
        network = build_wards_network(params=params,
                                      profiler=p,
                                      max_nodes=max_nodes,
                                      max_links=max_links,
                                      nthreads=nthreads)
        p = p.stop()

        # sanity-check that the network makes sense - there are specific
        # requirements for the data layout
        network.assert_sane(profiler=p)

        p = p.start("add_distances")
        from .utils._add_wards_network_distance \
            import add_wards_network_distance
        add_wards_network_distance(network, nthreads=nthreads)

        from .utils._console import Console
        p = p.stop()

        # add metadata about the wards
        p = p.start("add_lookup")
        network._add_lookup(nthreads=nthreads)
        p = p.stop()

        if params.input_files.seed:
            from .utils import read_done_file
            p = p.start("read_done_file")
            to_seed = read_done_file(params.input_files.seed)
            nseeds = len(to_seed)

            Console.print(to_seed)
            Console.print(f"Number of seeds equals {nseeds}")
            network.to_seed = to_seed
            p = p.stop()

        # By default, we initialise the network ready for a run,
        # namely make sure everything is reset and the population
        # is at work
        p = p.start("reset_everything")
        network.reset_everything(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.start("rescale_play_matrix")
        network.rescale_play_matrix(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.start("move_from_play_to_work")
        network.move_from_play_to_work(nthreads=nthreads, profiler=p)
        p = p.stop()

        if not p.is_null():
            p = p.stop()
            Console.print(str(p))

        Console.print(f"[bold]Network loaded. Population: {network.population}, "
                      f"Workers: {network.work_population}, Players: "
                      f"{network.play_population}[/]", markup=True)

        return network

    def num_demographics(self) -> int:
        """Return the number of demographics (always 1 for a Network).
           This function is added so that a single Network has
           the same functions as a multi-demographics Networks
        """
        return 1

    def copy(self):
        """Return a copy of this Network. Use this to hold a copy of
           the network that you can use to reset between runs
        """
        from copy import copy, deepcopy
        network = copy(self)

        network.nodes = self.nodes.copy()
        network.links = self.links.copy()
        network.play = self.play.copy()

        network.to_seed = deepcopy(self.to_seed)
        network.params = deepcopy(self.params)

        return network

    def assert_sane(self, profiler: None):
        """Assert that this network is sane. This checks that the network
           is laid out correctly in memory and that it doesn't have
           anything unexpected. Checking here will prevent us from having
           to check every time the network is accessed
        """
        from .utils import assert_sane_network
        assert_sane_network(network=self, profiler=profiler)

    def _add_lookup(self, lookup_function=None, nthreads: int = 1):
        """Read in the ward lookup information that is used to
           locate wards by name or region
        """
        if lookup_function is None:
            from .utils import add_lookup
            lookup_function = add_lookup

        lookup_function(self, nthreads=nthreads)

    def get_index(self, id: WardID) -> _Tuple[PersonType, int, int]:
        """Return the index of the Node or Link(s) that corresponds
           to the passed WardID.

           This returns a tuple of three values;

           (PersonType, start_idx, end_idx)

           If this is a worker, then it will either return the
           index of the Link for a specific work-link connection,
           or the range of indicies for all of the work links
           to this ward, so

           (PersonType.WORKER, link_idx, link_idx+!)  for a single link, or

           (PersonType.WORKER, link.begin_to, link.end_to) for all links

           If this is a player, then it will return the ID of the
           Node (which is the index of the Node in Nodes), and
           so

           (PersonType.PLAYER, node_index, node_index+1)

           This raises a KeyError if there is no ward or ward-link
           that matches the WardID
        """
        from .utils._network_functions import network_get_index
        return network_get_index(self, id)

    def get_node_index(self, index: _Union[str, int]):
        """Return the index of the node in this network that matches
           'index'. This could be an integer, in which case this
           will directly look up the index of the node in the
           Nodes, or else it could be a string, in which case
           the WardInfo will be used to identify the node and
           look up the index from there.
        """
        try:
            index = int(index)
        except Exception:
            pass

        if isinstance(index, int):
            return self.nodes.get_index(index)
        else:
            matches = self.info.find(index)

            if len(matches) == 0:
                from .utils._console import Console
                Console.error(f"Cannot find a ward that matches {index}")
                raise KeyError(f"Cannot find a ward that matches {index}")
            elif len(matches) > 1:
                # do we have a perfect single match?
                name = index.split("/")[0].strip()

                for match in matches:
                    if self.info[match].name == name:
                        # perfect match
                        return match

                from .utils._console import Console
                err = [f"Too many wards match {index}"]

                for match in matches:
                    err.append(f"* {self.info[match]}")

                err.append("Please narrow down your search to match one.")

                Console.error("\n".join(err), markdown=True)

                raise KeyError(
                    f"Cannot find a single ward that matches {index}")
            else:
                return matches[0]

    def initialise_infections(self, nthreads: int = 1):
        """Initialise and return the space that will be used
           to track infections
        """
        from ._infections import Infections
        return Infections.build(network=self)

    def recalculate_denominators(self, nthreads: int = 1, profiler=None):
        """Recalculate the denominators used in the calculation. This should
           be called after you have changed the population of the
           network, e.g. during a move function
        """
        from .utils._recalculate_denominators import \
            recalculate_play_denominator_day, \
            recalculate_work_denominator_day

        workers = recalculate_work_denominator_day(self, nthreads=nthreads,
                                                   profiler=profiler)
        players = recalculate_play_denominator_day(self, nthreads=nthreads,
                                                   profiler=profiler)

        self.work_population = workers
        self.play_population = players

        test_pop = int(self.work_population + self.play_population)

        if test_pop != self.population:
            from .utils._console import Console

            # this could be because individuals are in the NULL ward
            n_null = int(self.nodes.save_play_suscept[0]) + \
                self.links.weight[0]

            if test_pop + n_null != self.population:
                Console.error(
                    f"Disagreement in the population size: "
                    f"{int(self.work_population)}+"
                    f"{int(self.play_population)} == "
                    f"{test_pop} != {self.population}")

                raise AssertionError("Disagreement in population size")

    def get_min_max_distances(self, nthreads: int = 1,
                              profiler=None):
        """Calculate and return the minimum and maximum distances
           between nodes in the network
        """
        try:
            return self._min_max_distances
        except Exception:
            pass

        from .utils import get_min_max_distances
        self._min_max_distances = get_min_max_distances(network=self,
                                                        nthreads=nthreads)

        return self._min_max_distances

    def reset_everything(self, nthreads: int = 1,
                         profiler=None):
        """Resets the network ready for a new run of the model"""
        from .utils import reset_everything
        reset_everything(network=self, nthreads=nthreads, profiler=profiler)

    def update(self, params: Parameters, demographics=None, population=None,
               nthreads: int = 1, profiler=None):
        """Update this network with a new set of parameters
           ( and optionally demographics).

           This is used to update the parameters for the network
           for a new run. The network will be reset
           and ready for a new run.

           Parameters
           ----------
           params: Parameters
             The new parameters with which to update this Network
           demographics: Demographics
             The new demographics with which to update this Network.
             Note that this will return a Network object that contains
             the specilisation of this Network
           nthreads: int
             Number of threads over which to parallelise this update
           profiler: Profiler
             The profiler used to profile this update

           Returns
           -------
           network: Network or Networks
             Either this Network after it has been updated, or the
             resulting Networks from specialising this Network using
             Demographics
        """
        if profiler is None:
            from .utils._profiler import NullProfiler
            profiler = NullProfiler()

        p = profiler.start("Network.update")

        if self.name is None or \
                self.name not in params.specialised_demographics():
            self.params = params
        else:
            self.params = params[self.name]

        p = p.start("reset_everything")
        self.reset_everything(nthreads=nthreads, profiler=p)
        p = p.stop()

        if demographics:
            from .utils._worker import must_rebuild_network

            if must_rebuild_network(network=self, params=self.params,
                                    demographics=demographics):
                network = demographics.build(params=self.params,
                                             population=population,
                                             nthreads=nthreads,
                                             profiler=p)
            else:
                network = demographics.specialise(network=self,
                                                  profiler=p,
                                                  nthreads=nthreads)
        else:
            network = self

        p = p.start("rescale_play_matrix")
        network.rescale_play_matrix(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.start("move_from_play_to_work")
        network.move_from_play_to_work(nthreads=nthreads, profiler=p)
        p = p.stop()

        p = p.stop()

        return network

    def rescale_play_matrix(self, nthreads: int = 1,
                            profiler=None):
        """Rescale the play matrix"""
        from .utils import rescale_play_matrix
        rescale_play_matrix(network=self, nthreads=nthreads, profiler=profiler)

    def move_from_play_to_work(self, nthreads: int = 1,
                               profiler=None):
        """Move the population from play to work"""
        from .utils import move_population_from_play_to_work
        move_population_from_play_to_work(network=self, nthreads=nthreads,
                                          profiler=profiler)

    def has_different_work_matrix(self):
        """Return whether or not the sub-network work matrix
           is different to that of the overall network
        """
        return self._work_index is not None

    def get_work_index(self):
        """Return the mapping from the index in this sub-networks work
           matrix to the mapping in the overall network's work matrix
        """
        if self.has_different_work_matrix():
            # remember this is 1-indexed, so work_index[1] is the first
            # value
            return self._work_index
        else:
            return range(1, self.nlinks + 1)

    def specialise(self, demographic, profiler=None,
                   nthreads: int = 1):
        """Return a copy of this network that has been specialised
           for the passed demographic. The returned network will
           contain only members of that demographic, with the
           parameters of the network adjusted according to the rules
           of that demographic

           Parameters
           ----------
           demographic: Demographic
             The demographic with which to specialise

           Returns
           -------
           network: Network
             The specialised network
        """
        return demographic.specialise(network=self,
                                      profiler=profiler,
                                      nthreads=nthreads)

    def scale_susceptibles(self, ratio: any = None,
                           work_ratio: any = None, play_ratio: any = None):
        """Scale the number of susceptibles in this Network
           by the passed scale ratios. These can be values, e.g.
           ratio = 2.0 will scale the total number of susceptibles
           in each ward by 2.0. They can also be lists of values,
           where ward[i] will be scaled by ratio[i]. They can also
           be dictionaries, e.g. ward[i] scaled by ratio[i]

           Parameters
           ----------
           ratio: None, float, list or dict
             The amount by which to scale the total population of
             susceptibles - evenly scales the work and play populations
           work_ratio: None, float, list or dict
             Scale only the work population of susceptibles
           play_ratio: None, float, list or dict
             Scale only the play population of susceptibles

           Returns
           -------
           None
        """

        if ratio is not None:
            work_ratio = ratio
            play_ratio = ratio

        if work_ratio is not None:
            self.links.scale_susceptibles(work_ratio)

        self.nodes.scale_susceptibles(work_ratio=work_ratio,
                                      play_ratio=play_ratio)

    def to_wards(self, profiler=None, nthreads: int = 1):
        """Return the ward-level data in this network converted to
           a Wards object. This supports editing and save/restore
           to JSON
        """
        from .utils._network_wards import save_to_wards
        return save_to_wards(self, profiler=profiler, nthreads=nthreads)

    @staticmethod
    def from_wards(wards, params: Parameters = None,
                   disease: Disease = None,
                   profiler=None,
                   nthreads: int = 1):
        """Construct a Network from the passed Wards object(e.g. after
           editing, or restoring from JSON
        """
        from .utils._network_wards import load_from_wards
        return load_from_wards(wards, params=params, disease=disease,
                               profiler=profiler, nthreads=nthreads)

    def run(self, population: Population,
            output_dir: OutputFiles,
            seed: int = None,
            nsteps: int = None,
            nthreads: int = None,
            iterator=None,
            extractor=None,
            mixer=None,
            mover=None,
            profiler=None) -> Population:
        """Run the model simulation for the passed population.
           The random number seed is given in 'seed'. If this
           is None, then a random seed is used.

           All output files are written to 'output_dir'

           The simulation will continue until the infection has
           died out or until 'nsteps' has passed(keep as 'None'
           to prevent exiting early).

           Parameters
           - ---------
           population: Population
             The initial population at the start of the model outbreak.
             This is also used to set start date and day of the model
             outbreak
           output_dir: OutputFiles
             The directory to write all of the output into
           seed: int
             The random number seed used for this model run. If this is
             None then a very random random number seed will be used
           nsteps: int
             The maximum number of steps to run in the outbreak. If None
             then run until the outbreak has finished
           profiler: Profiler
             The profiler to use - a new one is created if one isn't passed
           nthreads: int
             Number of threads over which to parallelise this model run
           iterator: function
             Function that is called at each iteration to get the functions
             that are used to advance the model
           extractor: function
             Function that is called at each iteration to get the functions
             that are used to extract data for analysis or writing to files
           mixer: function
             Function that is used to mix demographic data. Not used
             by a single Network(used by Networks)
           mover: function
             Function that is used to move the population between different
             demographics. Not used by a single Network(used by Networks)
        """
        # Create the random number generator
        from .utils._ran_binomial import seed_ran_binomial, ran_binomial

        if seed == 0:
            # this is a special mode that a developer can use to force
            # all jobs to use the same random number seed (15324) that
            # is used for comparing outputs. This should NEVER be used
            # for production code
            from .utils._console import Console
            Console.warning("Using special mode to fix all random number "
                            "seeds to 15324. DO NOT USE IN PRODUCTION!!!")
            seed = 15324
            rng = seed_ran_binomial(seed=seed)
        else:
            rng = seed_ran_binomial(seed=seed)

        # Print the first five random numbers so that we can
        # compare to other codes/runs, and be sure that we are
        # generating the same random sequence
        randnums = []
        for i in range(0, 5):
            randnums.append(str(ran_binomial(rng, 0.5, 100)))

        from .utils._console import Console

        Console.print(
            f"* Using random number seed {seed}\n"
            f"* First five random numbers equal **{'**, **'.join(randnums)}**",
            markdown=True)
        randnums = None

        if nthreads is None:
            from .utils._parallel import get_available_num_threads
            nthreads = get_available_num_threads()

        from .utils._parallel import create_thread_generators
        rngs = create_thread_generators(rng, nthreads)

        # Create space to hold the results of the simulation
        infections = self.initialise_infections()

        if nthreads == 1:
            s = ""
        else:
            s = "s"

        Console.rule(f"Running the model using {nthreads} thread{s}")

        from .utils import run_model
        population = run_model(network=self,
                               population=population,
                               infections=infections,
                               rngs=rngs, output_dir=output_dir,
                               nsteps=nsteps,
                               nthreads=nthreads,
                               profiler=profiler,
                               iterator=iterator, extractor=extractor,
                               mover=mover, mixer=mixer)

        return population
