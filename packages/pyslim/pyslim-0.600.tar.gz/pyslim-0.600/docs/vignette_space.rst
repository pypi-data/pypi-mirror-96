.. _sec_vignette_space:


==============================
Vignette: A spatial simulation
==============================

Here we'll talk through a typical workflow with pyslim,
which will:

1. Simulate data with SLiM, remembering some ancestral individuals.
2. Recapitate and mutate.
3. Take a subsample of the modern and ancestral individuals.
4. Get these individual locations and make a map.
5. Compute divergences between individuals, and plot against geographic distance.
6. Write out a VCF file of these individuals' genotypes and other data for use by other programs.


**********
Simulation
**********

Here is a simple spatial SLiM recipe that simulates 1000 individuals on a spatial landscape.
The focus of this vignette is not on SLiM, so we won't go into detail here.
Here are notes:

1. It does not have *any* mutations: we'll add these on afterwards.
2. There is local fecundity regulation of population density: individuals with more neighbors
   have fewer offspring.
3. We run the simulation for 2000 time steps, and "remember" everyone who is alive at time step 1000.

.. literalinclude:: vignette_space.slim


Ok, now let's have a quick look at the output:

.. code-block:: python

   import pyslim, tskit
   import numpy as np

   slim_ts = pyslim.load("spatial_sim.trees")
   print(f"The tree sequence has {slim_ts.num_trees} trees on a genome of length {slim_ts.sequence_length},"
         f" {slim_ts.num_individuals} individuals, {slim_ts.num_samples} 'sample' genomes,"
         f" and {slim_ts.num_mutations} mutations.")

Running this code, we get

.. code-block:: none

   The tree sequence has 37095 trees on a genome of length 100000000.0,
   2712 individuals, 5424 'sample' genomes, and 0 mutations.


It makes sense we have no mutations: we haven't added any yet.
The tree sequence is recording the relationship between 5,424 genomes (the "samples"),
which requires 37,095 distinct trees along the genome.
Individuals are diploid, which explains why the number of individuals
is equal to half the number of samples.
Let's have a look at how old those individuals are,
by tabulating when they were born:

.. code-block:: python

   for t in np.unique(slim_ts.individual_times):
     print(f"There are {np.sum(slim_ts.individual_times == t)} individuals from time {t}.")
   
This gets us

.. code-block:: none

    There are 687 individuals from time 0.0.
    There are 343 individuals from time 1.0.
    There are 167 individuals from time 2.0.
    There are 94 individuals from time 3.0.
    There are 44 individuals from time 4.0.
    There are 27 individuals from time 5.0.
    There are 9 individuals from time 6.0.
    There are 4 individuals from time 7.0.
    There are 1 individuals from time 8.0.
    There are 2 individuals from time 9.0.
    There are 668 individuals from time 1000.0.
    There are 334 individuals from time 1001.0.
    There are 165 individuals from time 1002.0.
    There are 84 individuals from time 1003.0.
    There are 51 individuals from time 1004.0.
    There are 10 individuals from time 1005.0.
    There are 11 individuals from time 1006.0.
    There are 6 individuals from time 1007.0.
    There are 2 individuals from time 1008.0.
    There are 1 individuals from time 1009.0.
    There are 2 individuals from time 1010.0.


These "times" record the birth times of each individual.
These are *tskit* times, which are in units of "time ago",
so for instance, there are 343 individuals born one time unit before the end of the simulation
and 167 born two time units before the end of the simulation.
(This confusing choice of units is because tskit was developed for msprime, a coalescent simulator.)
This also tells us that there's a bunch of individuals born around 1000 time steps ago,
when we asked SLiM to Remember everyone alive at the time,
and some more in the past few time steps, i.e., the present.
This is a non-Wright-Fisher simulation,
and so individuals may live for more than one time step (even up to age 10, it seems).
Let's check that all these individuals are alive at either (a) today or (b) 1000 time steps ago.

.. code-block:: python

   for t in [0, 1000]:
      alive = slim_ts.individuals_alive_at(t)
      print(f"There were {len(alive)} individuals alive {t} time steps in the past.")


This tells us that

.. code-block:: none

    There were 1378 individuals alive 0 time steps in the past.
    There were 1334 individuals alive 1000 time steps in the past.

And, 1378 + 1334 is 2712, the total number of individuals.
So, this all checks out.


*************************
Recapitation and mutation
*************************

Next, we want to (a) simulate some ancestral diversity and (b) add in neutral mutations.
Please see `Haller et al (2019) <https://onlinelibrary.wiley.com/doi/abs/10.1111/1755-0998.12968>`_
for the why and how of these steps.
But, first let's see if recapitation is necessary:
on how much of the genome is the tree sequence not coalesced?
In other words, recapitation adds diversity present in the initial generation;
will it make a difference? 
In fact, *no* segments of the genome have coalesced:

.. code-block:: none

   >> sum([t.num_roots == 1 for t in slim_ts.trees()])
   0
   >>> sum([t.num_roots > 0 for t in slim_ts.trees()])
   37095

Next, we will:

1. Recapitate, running a coalescent simulation to build ancestral trees.
2. Mutate, adding neutral variation.
3. Save the resulting tree sequence to disk for future use.

We *won't* simplify, since we may as well keep around all the information.
But, if we did (e.g., if we were running a large number of simulations),
we would need to pass ``keep_input_roots=True`` to allow recapitation. 

.. note::

   The units of time in the tree sequence are SLiM's "time steps", and
   so are not necessarily equal to the mean generation time in a
   non-Wright-Fisher model. Per-generation rates need to be divided by the
   mean generation time, which can be measured in SLiM.

.. code-block:: python

   import msprime

   recap_ts = slim_ts.recapitate(recombination_rate=1e-8, Ne=1000)
   ts = pyslim.SlimTreeSequence(
         msprime.mutate(recap_ts, rate=1e-8, keep=True))
   ts.dump("spatial_sim.recap.trees")

   print(f"The tree sequence now has {ts.num_trees} trees,"
         f" and {ts.num_mutations} mutations.")


This has added mutations according to an infinite-sites model of mutation,
resulting in

.. code-block:: none

    The tree sequence now has 45160 trees, and 93280 mutations.

.. note::

   Since :meth:`mutate <msprime.mutate>` is an msprime method, it does not return a pyslim
   tree sequence, so we need to convert it back, by wrapping the call to `mutate`
   in :func:`.SlimTreeSequence`.

We will have no further use for ``slim_ts`` or for ``recap_ts``;
we've just given them separate names for tidiness.
And, since the original SLiM mutation had no mutations, we didn't need to specify ``keep=True``
in :meth:`mutate <msprime.mutate>`, but if we *had* put down selected mutations with SLiM
we'd probably want to keep them around.


****************************
Take a sample of individuals
****************************

Now it's time to compute some things.
In real life we don't get to work with *everyone* usually,
so we'll take a subset of individuals.
The range we have simulated has width and height 35 units,
with a population density of around 1 per unit area.
We'll get genomes to work with by pulling out

1. All the modern individuals in the five squares of width 5 in the corners of the range
   and the center, and
2. Five individuals sampled randomly from everyone alive 1000 time steps ago.

.. code-block:: python


   np.random.seed(23)

   alive = ts.individuals_alive_at(0)
   locs = ts.individual_locations[alive, :]

   W = 35
   w = 5
   groups = {
      'topleft' : alive[np.logical_and(locs[:, 0] < w, locs[:, 1] < w)],
      'topright' : alive[np.logical_and(locs[:, 0] < w, locs[:, 1] > W - w)],
      'bottomleft' : alive[np.logical_and(locs[:, 0] > W - w, locs[:, 1] < w)],
      'bottomright' : alive[np.logical_and(locs[:, 0] > W - w, locs[:, 1] > W - w)],
      'center' : alive[np.logical_and(np.abs(locs[:, 0] - W/2) < w/2,
                                      np.abs(locs[:, 1] - W/2) < w/2)]
      }

   old_ones = ts.individuals_alive_at(1000)
   groups['ancient'] = np.random.choice(old_ones, size=5)

   for k in groups:
      print(f"We have {len(groups[k])} individuals in the {k} group.")


.. code-block:: none

    We have 36 individuals in the topleft group.
    We have 34 individuals in the topright group.
    We have 30 individuals in the bottomleft group.
    We have 29 individuals in the bottomright group.
    We have 24 individuals in the center group.
    We have 5 individuals in the ancient group.

To keep names associated with each subset of individuals,
we've kept the individuals in a dict, so that for instance
``groups["topleft"]`` is an array of all the individual IDs that are in the top left corner.
The IDs of the ancient individuals we will work with are kept in the array ``ancient``.

Let's do a quick consistency check, that everyone in ``ancient`` was actually born around 1000 time steps ago:

.. code-block:: python

   for i in groups["ancient"]:
      ind = ts.individual(i)
      assert(ind.time >= 1000 and ind.time < 1020)

That checks out.

******************
Plotting locations
******************

We should check this: plot where these individuals lie
relative to everyone else.
The individuals locations are available as a property of individuals,
but to make things easier, it's also present in a `num_individuals x 3`
numpy array as ``ts.individual_locations``.
(There are three columns because SLiM allows for
`(x, y, z)` coordinates, but we'll just use the first two.)
Since ``groups["topleft"]`` is an array of individual IDs,
we can pull out the locations of the "topleft" individuals
by indexing the rows of the individual location array:

.. code-block:: none

   >>> ts.individual_locations
    array([[12.95327106, 10.6956274 ,  0.        ],
           [10.45240784, 34.81249943,  0.        ],
           [26.2278031 , 23.20632444,  0.        ],
           ...,
           [30.21201837, 20.9920904 ,  0.        ],
           [ 1.38658573, 17.6933384 ,  0.        ],
           [ 5.42651858, 12.30457856,  0.        ]])
   >>> ts.individual_locations.shape
   (2712, 3)
   >>> ts.individual_locations[groups["topleft"], :].shape
   (9, 3)


Using this, we can easily plot the locations of all the individuals from today
(on the left) and 1000 time steps ago (on the right).
We have to do a bit of mucking around to set the colors so that they reflect
which group each individual is in.

.. code-block:: python

   import matplotlib
   matplotlib.use('Agg')
   import matplotlib.pyplot as plt

   group_order = ['topleft', 'topright', 'bottomleft', 'bottomright', 'center', 'ancient']
   ind_colors = np.repeat(0, ts.num_individuals)
   for j, k in enumerate(group_order):
      ind_colors[groups[k]] = 1 + j

   old_locs = ts.individual_locations[old_ones, :]

   fig = plt.figure(figsize=(12, 6), dpi=300)
   ax = fig.add_subplot(121)
   ax.set_title("today")
   ax.scatter(locs[:,0], locs[:,1], s=20, c=ind_colors[alive])
   ax = fig.add_subplot(122)
   ax.set_title("long ago")
   ax.scatter(old_locs[:, 0], old_locs[:, 1], s=20, c=ind_colors[old_ones])
   fig.savefig("spatial_sim_locations.png")


.. image:: _static/spatial_sim_locations.png
   :width: 1200px
   :alt: Spatial location of all individuals and the genotyped ones.



*********************
Isolation by distance
*********************

Now, let's look at *isolation by distance*, i.e.,
let's compare geographic and genetic distances.
Here, "genetic distance" will be mean pairwise sequence divergence.
First, we'll compute mean genetic distance between each of our five groups.

The first thing we need to do is some bookkeeping.
So far, we've just worked with *individuals*,
but tree sequence tools, in particular the statistics computation methods from tskit,
are designed to work with *genomes*, also known as "nodes".
So, first we need to pull out the *node IDs* corresponding to the individuals we want.
The things that make up a tree sequence - individuals, nodes, mutations, etcetera -
can generally be examined individually. 
For instance, here's what we have for the five "ancient" individuals:

.. code-block:: none

   >>> for i in groups['ancient']:
   ...   print(ts.individual(i))
   ... 
   {'id': 1427, 'flags': 131072, 'location': array([24.6693165,  0.4198795,  0.       ]),
    'nodes': array([98, 99], dtype=int32), 'population': 1, 'time': 1004.0,
    'metadata': {'pedigree_id': 1299347, 'age': 4, 'subpopulation': 1, 'sex': -1, 'flags': 0}}
   {'id': 1837, 'flags': 131072, 'location': array([21.3849923 , 12.74527713,  0.        ]),
    'nodes': array([918, 919], dtype=int32), 'population': 1, 'time': 1001.0,
    'metadata': {'pedigree_id': 1303415, 'age': 1, 'subpopulation': 1, 'sex': -1, 'flags': 0}}
   {'id': 2594, 'flags': 131072, 'location': array([13.17510948, 27.74727477,  0.        ]),
    'nodes': array([2432, 2433], dtype=int32), 'population': 1, 'time': 1000.0,
    'metadata': {'pedigree_id': 1305382, 'age': 0, 'subpopulation': 1, 'sex': -1, 'flags': 0}}
   {'id': 2414, 'flags': 131072, 'location': array([17.50087554, 19.63608325,  0.        ]),
    'nodes': array([2072, 2073], dtype=int32), 'population': 1, 'time': 1000.0,
    'metadata': {'pedigree_id': 1305045, 'age': 0, 'subpopulation': 1, 'sex': -1, 'flags': 0}}
   {'id': 1911, 'flags': 131072, 'location': array([9.6343188 , 6.82903893, 0.        ]),
    'nodes': array([1066, 1067], dtype=int32), 'population': 1, 'time': 1001.0,
    'metadata': {'pedigree_id': 1303711, 'age': 1, 'subpopulation': 1, 'sex': -1, 'flags': 0}}

Notice that among other things, each individual carries around a list of their node IDs,
i.e., their genomes.
We need to put these all in a list of lists,
so that, for instance, the first element of the list will have the node IDs of all the genomes
of the individuals in the "topleft" group.
And, since we kept the individual IDs in a dict, which are unordered,
we'll have to do some extra work to make sure we keep track of order.

.. code-block:: python

   sampled_nodes = [[] for _ in groups]
   for j, k in enumerate(group_order):
      for ind in groups[k]:
         sampled_nodes[j].extend(ts.individual(ind).nodes)

Let's do a consistency check: the number of nodes in each element of this list
should be twice the number of individuals in the corresponding list.

.. code-block:: none

   >>> [len(groups[k]) for k in groups]
   [9, 12, 13, 10, 6, 5]

   >>> [len(u) for u in sampled_nodes]
   [18, 24, 26, 20, 12, 10]
   
So, in the 'topleft' corner there are 12 diploids. That checks out.   

Now, we can compute the matrix of pairwise mean sequence divergences
between and within these sets.
This is done using the :meth:`ts.divergence <tskit.TreeSequence.divergence>` method.

.. code-block:: python

   pairs = [(i, j) for i in range(6) for j in range(6)]
   group_div = ts.divergence(sampled_nodes, indexes=pairs).reshape((6, 6))

   print("\t" + "\t".join(group_order))
   for i, group in enumerate(group_order):
      print(f"{group_order[i]}:\t" + "\t".join(map(str, np.round(group_div[i], 7))))


.. code-block:: none

    topleft:     3.69e-05    5.58e-05    5.57e-05    6.03e-05    5.56e-05    5.9e-05
    topright:    5.58e-05    3.86e-05    5.83e-05    5.83e-05    5.55e-05    6.06e-05
    bottomleft:  5.57e-05    5.83e-05    4.5e-05     5.79e-05    5.63e-05    6.02e-05
    bottomright: 6.03e-05    5.83e-05    5.79e-05    3.18e-05    5.6e-05     6.14e-05
    center:      5.56e-05    5.55e-05    5.63e-05    5.6e-05     4.73e-05    6.09e-05
    ancient:     5.9e-05     6.06e-05    6.02e-05    6.14e-05    6.09e-05    4.56e-05


That's nice, but to look at isolation by distance,
we should actually separate out the individuals.
To do that, we need to create a list of lists of nodes
whose j-th entry is the nodes belonging to the j-th individual,
and to keep track of which group each one belongs to.

.. code-block:: python

   ind_nodes = []
   ind_group = []
   ind_ids = []
   for j, group in enumerate(group_order):
      for ind in groups[group]:
         ind_ids.append(ind)
         ind_nodes.append(ts.individual(ind).nodes)
         ind_group.append(group_order[j])

   nind = len(ind_ids)
   pairs = [(i, j) for i in range(nind) for j in range(i, nind)]
   ind_div = ts.divergence(ind_nodes, indexes=pairs)

Here we've only computed divergences in the *upper triangle* of the pairwise divergence matrix,
with heterozygosities on the diagonal.
We'll also need pairwise geographic distances:

.. code-block:: python

   geog_dist = np.repeat(0.0, len(pairs))
   locs = ts.individual_locations
   for k, (i, j) in enumerate(pairs):
      geog_dist[k] = np.sqrt(np.sum((locs[ind_ids[i], :] - locs[ind_ids[j], :])**2))

Let's check that makes sense: distances of individuals from themselves should be zero.

.. code-block:: python

   for (i, j), x in zip(pairs, geog_dist):
     if i == j:
       assert(x == 0)

Python does not complain, which is good.
Now let's plot genetic distance against geographic distance.

.. code-block:: python

   pair_colors = np.repeat(0, len(pairs))
   for k, (i, j) in enumerate(pairs):
      if ind_group[i] == "ancient" or ind_group[j] == "ancient":
         pair_colors[k] = 1

   fig = plt.figure(figsize=(6, 6), dpi=300)
   ax = fig.add_subplot(111)
   ax.scatter(geog_dist, 1e3 * ind_div, s=20, alpha=0.5,
              c=pair_colors)
   ax.set_xlabel("geographic distance")
   ax.set_ylabel("genetic distance (diffs/Kb)")
   fig.savefig("spatial_sim_ibd.png")


.. image:: _static/spatial_sim_ibd.png
   :width: 600px
   :alt: Geographic and genetic distances in the simulation.


Since we multiplied ``ind_div`` by 1,000,
the units of genetic distance are in mean number of nucleotide differences per kilobase.
It is clear that closer samples are more closely related,
and the distinct clusters corresponding to the five sampled boxes are visible.
Furthermore, ancient samples are generally more distantly diverged.



**********
VCF output
**********

Now we want to write out these data for analysis with other programs.
To do this, and make sure that everything stays nicely cross-referenced,
we're going to loop through the sampled individuals, writing their information to a file,
while at the same time constructing a list of individual IDs,
whose genomes we will write out to a VCF file.

.. code-block:: python

   indivlist = []
   indivnames = []
   with open("spatial_sim_individuals.txt", "w") as indfile:
     indfile.writelines("\t".join(["vcf_label", "tskit_id", "slim_id"]
                                  + ["birth_time_ago", "age", "x", "y"]) + "\n")
     for group in group_order:
        for i in groups[group]:
           indivlist.append(i)
           ind = ts.individual(i)
           vcf_label = f"tsk_{ind.id}"
           indivnames.append(vcf_label)
           data = [vcf_label, str(ind.id), str(ind.metadata["pedigree_id"]), str(ind.time),
                   str(ind.metadata["age"]), str(ind.location[0]), str(ind.location[1])]
           indfile.writelines("\t".join(data) + "\n")

   with open("spatial_sim_genotypes.vcf", "w") as vcffile:
     ts.write_vcf(vcffile, individuals=indivlist, individual_names=indivnames)


****************
More information
****************

1. The distinction between "nodes" (i.e., genomes) and "individuals" can be confusing,
   as well as the idea of "samples".
   Please see the
   `tskit documentation <https://tskit.readthedocs.io/en/latest/data-model.html>`_
   for more explanation about these concepts.

2. The general interface for computing statistics (explaining, for instance, the "indexes"
   argument above) is described in
   `the tskit documentation <https://tskit.readthedocs.io/en/latest/stats.html>`_
   also.


**************************
What about simplification?
**************************

The tree sequence we worked with here contains more information than we need,
including the first generation individuals.
If we wanted to remove this, we could have used the
:meth:`simplify <tskit.TreeSequence.simplify>` method,
which reduced the tree sequence to the minimal required to record the information
about a provided set of nodes.
In the workflow above we didn't ever *simplify* the tree sequence,
because we didn't need to.
Because simplify reorders nodes and removes unused individuals and populations,
it requires an extra layer of bookkeeping.
Such relabeling also makes it harder to compare results across different analyses
of the same data.

Simplifying the tree sequence down to the nodes of the individuals
in our "groups" would not change any subsequent analysis (except perhaps
removing monomorphic sites in the VCF output),
and would speed up computation of diversity.
Since the calculation was fast already, it wasn't worth it in this case,
but for much larger tree sequences it could be worth the extra code complexity.

