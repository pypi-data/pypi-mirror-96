..
   # ==============================================================================
   # author          :Ghislain Vieilledent
   # email           :ghislain.vieilledent@cirad.fr, ghislainv@gmail.com
   # web             :https://ecology.ghislainv.fr
   # license         :GPLv3
   # ==============================================================================

.. image:: https://ecology.ghislainv.fr/forestatrisk/_static/logo-far.svg
   :align: right
   :target: https://ecology.ghislainv.fr/forestatrisk
   :alt: Logo forestatrisk
   :width: 140px

``forestatrisk`` Python package
*******************************


|Python version| |PyPI version| |GitHub Actions| |License| |Zenodo| |JOSS|


Overview
========

The ``forestatrisk`` Python package can be used to **model** the
tropical deforestation spatially, **predict** the spatial risk of
deforestation, and **forecast** the future forest cover in the
tropics. It provides functions to estimate the spatial probability of
deforestation as a function of various spatial explanatory variables.

Spatial explanatory variables can be derived from topography
(altitude, slope, and aspect), accessibility (distance to roads,
towns, and forest edge), deforestation history (distance to previous
deforestation), or land conservation status (eg. protected area) for
example.

.. image:: https://ecology.ghislainv.fr/forestatrisk/_static/forestatrisk.png
   :align: center
   :target: https://ecology.ghislainv.fr/forestatrisk
   :alt: prob_AFR
   :width: 800px

Statement of Need
=================

Spatial modelling of the deforestation allows identifying the main
factors determining the spatial risk of deforestation and quantifying
their relative effects. Forecasting forest cover change is paramount
as it allows anticipating the consequences of deforestation (in terms
of carbon emissions or biodiversity loss) under various technological,
political and socio-economic scenarios, and informs decision makers
accordingly. Because both biodiversity and carbon vary greatly in
space, it is necessary to provide spatial forecasts of forest cover
change to properly quantify biodiversity loss and carbon emissions
associated with future deforestation.

The ``forestatrisk`` Python package can be used to model the tropical
deforestation spatially, predict the spatial risk of deforestation,
and forecast the future forest cover in the tropics. The spatial data
used to model deforestation come from georeferenced raster files,
which can be very large (several gigabytes). The functions available
in the ``forestatrisk`` package process large rasters by blocks of
data, making calculations fast and efficient. This allows
deforestation to be modeled over large geographic areas (e.g. at the
scale of a country) and at high spatial resolution
(eg. ≤ 30 m). The ``forestatrisk`` package offers the possibility
of using logistic regression with auto-correlated spatial random
effects to model the deforestation process. The spatial random effects
make possible to structure the residual spatial variability of the
deforestation process, not explained by the variables of the model and
often very large. In addition to these new features, the
``forestatrisk`` Python package is open source (GPLv3 license),
cross-platform, scriptable (via Python), user-friendly (functions
provided with full documentation and examples), and easily extendable
(with additional statistical models for example). The ``forestatrisk``
Python package has been used to model deforestation and predict future
forest cover by 2100 across the humid tropics
(`<https://forestatrisk.cirad.fr>`__).

Installation
============

You will need several dependencies to run the ``forestatrisk`` Python
package. The best way to install the package is to create a Python
virtual environment, either through ``conda`` (recommended) or ``virtualenv``.

Using ``conda`` (recommended)
+++++++++++++++++++++++++++++

You first need to have ``miniconda3`` installed (see `here
<https://docs.conda.io/en/latest/miniconda.html>`__).

Then, create a conda environment (details `here
<https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html>`__)
and install the ``forestatrisk`` package with the following commands:

.. code-block:: shell
		
   conda create --name conda-far python=3.7 gdal numpy matplotlib pandas patsy pip statsmodels --yes
   conda activate conda-far
   conda install -c conda-forge earthengine-api --yes
   pip install pywdpa sklearn # Packages not available with conda
   pip install forestatrisk # For PyPI version
   # pip install https://github.com/ghislainv/forestatrisk/archive/master.zip # For GitHub dev version
   # conda install -c conda-forge python-dotenv rclone --yes  # Potentially interesting libraries

To deactivate and delete the conda environment:

.. code-block:: shell
		
   conda deactivate
   conda env remove --name conda-far

Using ``virtualenv``
++++++++++++++++++++

You first need to have the ``virtualenv`` package installed (see `here <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`__).

Then, create a virtual environment and install the ``forestatrisk``
package with the following commands:

.. code-block:: shell

   cd ~
   mkdir venvs # Directory for virtual environments
   cd venvs
   virtualenv --python=/usr/bin/python3 venv-far
   source ~/venvs/venv-far/bin/activate
   # Install numpy first
   pip install numpy
   # Install gdal (the correct version) 
   pip install --global-option=build_ext --global-option="-I/usr/include/gdal" gdal==$(gdal-config --version)
   pip install forestatrisk # For PyPI version, this will install all other dependencies
   # pip install https://github.com/ghislainv/forestatrisk/archive/master.zip # For GitHub dev version
   pip install statsmodels # Optional additional packages

To deactivate and delete the virtual environment:

.. code-block:: shell
		
   deactivate
   rm -R ~/venvs/venv-far # Just remove the repository

Installation testing
++++++++++++++++++++

You can test that the package has been correctly installed using the
command ``forestatrisk`` in a terminal:

.. code-block:: shell

  forestatrisk

This should return a short description of the ``forestatrisk`` package
and the version number:

.. code-block:: shell

  # forestatrisk: modelling and forecasting deforestation in the tropics.
  # https://ecology.ghislainv.fr/forestatrisk/
  # forestatrisk version x.x.

You can also test the package executing the commands in the `Get
started
<https://ecology.ghislainv.fr/forestatrisk/notebooks/get_started.html>`__
tutorial.
   
Main functionalities
====================

Sample
++++++

Function ``.sample()`` sample observations points from a forest cover
change map. The sample is balanced and stratified between deforested
and non-deforested pixels. The function also retrieves information
from explanatory variables for each sampled point. Sampling is done by
block to allow computation on large study areas (e.g. country or
continental scale) with a high spatial resolution (e.g. 30m).

Model
+++++

Function ``.model_binomial_iCAR()`` can be used to fit the
deforestation model. A linear Binomial logistic regression model is
used in this case. The model includes an intrinsic Conditional
Autoregressive (iCAR) process to account for the spatial
autocorrelation of the observations. Parameter inference is done in a
hierarchical Bayesian framework. The function calls a Gibbs sampler
with a Metropolis algorithm written in pure C code to reduce
computation time.

Other models (such as a simple GLM or a Random Forest model) can also
be used.

Predict and project
+++++++++++++++++++

Function ``.predict()`` allows predicting the deforestation
probability on the whole study area using the deforestation model
fitted with ``.model_*()`` functions. The prediction is done by block
to allow the computation on large study areas (e.g. country or
continental scale) with a high spatial resolution (e.g. 30m).

Function ``.deforest()`` predicts the future forest cover map based on a
raster of probability of deforestation (rescaled from 1 to 65535),
which is obtained from function ``.predict()``, and an area (in
hectares) to be deforested.

Validate
++++++++

A set of functions (eg. ``.cross_validation()`` or
``.map_accuracy()``\ ) is also provided to perform model and map
validation.

Contributing
============

The ``forestatrisk`` Python package is Open Source and released under
the `GNU GPL version 3 license
<https://ecology.ghislainv.fr/forestatrisk/license.html>`__. Anybody
who is interested can contribute to the package development following
our `Community guidelines
<https://ecology.ghislainv.fr/forestatrisk/contributing.html>`__. Every
contributor must agree to follow the project's `Code of conduct
<https://ecology.ghislainv.fr/forestatrisk/code_of_conduct.html>`__.


.. |Python version| image:: https://img.shields.io/pypi/pyversions/forestatrisk?logo=python&logoColor=ffd43b&color=306998
   :target: https://pypi.org/project/forestatrisk
   :alt: Python version

.. |PyPI version| image:: https://img.shields.io/pypi/v/forestatrisk
   :target: https://pypi.org/project/forestatrisk
   :alt: PyPI version

.. |GitHub Actions| image:: https://github.com/ghislainv/forestatrisk/workflows/PyPkg/badge.svg
   :target: https://github.com/ghislainv/forestatrisk/actions
   :alt: GitHub Actions
	 
.. |License| image:: https://img.shields.io/badge/licence-GPLv3-8f10cb.svg
   :target: https://www.gnu.org/licenses/gpl-3.0.html
   :alt: License GPLv3	 

.. |Zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.996337.svg
   :target: https://doi.org/10.5281/zenodo.996337
   :alt: Zenodo

.. |JOSS| image:: https://joss.theoj.org/papers/b8fe1d3815c7385a1c3e454270bee041/status.svg
   :target: https://joss.theoj.org/papers/b8fe1d3815c7385a1c3e454270bee041
   :alt: JOSS
