# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kipet',
 'kipet.common',
 'kipet.core_methods',
 'kipet.dev_tools',
 'kipet.mixins',
 'kipet.model_components',
 'kipet.nsd_funs',
 'kipet.post_model_build',
 'kipet.top_level',
 'kipet.variance_methods',
 'kipet.visuals']

package_data = \
{'': ['*']}

install_requires = \
['Pint>=0.16.1,<0.17.0',
 'PyYAML>=5.4.1,<6.0.0',
 'Pyomo>=5.7.3,<6.0.0',
 'attrs>=20.3.0,<21.0.0',
 'ipopt>=0.3.0,<0.4.0',
 'matplotlib>=3.3.4,<4.0.0',
 'numpy>=1.20.1,<2.0.0',
 'pandas>=1.2.2,<2.0.0',
 'plotly>=4.14.3,<5.0.0',
 'scipy>=1.6.0,<2.0.0',
 'six>=1.15.0,<2.0.0']

setup_kwargs = {
    'name': 'kipet',
    'version': '0.2.0',
    'description': 'An all-in-one tool for fitting kinetic models using spectral and other state data',
    'long_description': '# <img alt="KIPET" src="branding/kipetlogo_full.svg" height="60">\n\n[![](https://img.shields.io/github/license/salvadorgarciamunoz/kipet)](https://github.com/salvadorgarciamunoz/kipet/blob/master/LICENSE)\n[![](https://img.shields.io/github/last-commit/salvadorgarciamunoz/kipet)](https://github.com/salvadorgarciamunoz/kipet/)\n[![](https://img.shields.io/pypi/wheel/kipet)](https://pypi.org/manage/project/kipet/release/0.1.1/)\n\n\nKIPET is a Python package designed to simulate, and estimate parameters from \nchemical reaction systems through the use of maximum likelihood principles,\nlarge-scale nonlinear programming and discretization methods. \n\n- **Documentation:** - https://kipet.readthedocs.io\n- **Examples and Tutorials** - https://github.com/kwmcbride/kipet_examples\n- **Source code:** - https://github.com/salvadorgarciamunoz/kipet\n- **Bug reports:** - https://github.com/salvadorgarciamunoz/kipet/issues\n\nIt has the following functionality:\n\n - Simulate a reactive system described with DAEs\n - Solve the DAE system with collocation methods\n - Pre-process data\n - Estimate variances of noise from the model and measurements\n - Estimate kinetic parameters from spectra or concentration data across 1 or \n  multiple experiments with different conditions\n - Estimate confidence intervals of the estimated parameters\n - Able to estimate variances and parameters for problems where there is dosing / inputs into the system\n - Provide a set of tools for estimability analysis\n - Allows for wavelength selection of most informative wavelengths from a dataset\n - Visualize results\n\n\n<br>\n\n## Installation\n\nThere are many options for installing KIPET.\n\n### PyPi\n[![](https://img.shields.io/badge/Install%20with-pip-green)]()\n[![](https://img.shields.io/pypi/v/kipet.svg?style=flat)](https://pypi.org/pypi/kipet/)\n<br>\n\nA packaged version of KIPET can be installed using:\n\n    pip install kipet\n\nIf you run into errors when installing KIPET using pip (such as when installing into a clean virtual environment), try installing the following packages beforehand:\n\n    pip install Cython numpy six\n    pip install kipet\n\n### Anaconda \n[![](https://anaconda.org/kwmcbride/kipet/badges/installer/conda.svg)]()\n[![Anaconda-Server Badge](https://img.shields.io/conda/vn/kwmcbride/kipet)](https://anaconda.org/kwmcbride/kipet)\n[![](https://img.shields.io/conda/pn/kwmcbride/kipet?color=orange)]()\n\n\nIf you are using Anaconda, KIPET can be installed using:\n\n    conda install -c kwmcbride kipet\n\nThe anaconda packages have the benefit of including pynumero ready to go, which is needed for some of the methods included in KIPET. You will need to compile these on your own if you choose to install KIPET using a different method. See the [pynumero readme](https://github.com/Pyomo/pyomo/tree/master/pyomo/contrib/pynumero) for more information. Otherwise, you can also use [k_aug](https://github.com/dthierry/k_aug) for these methods as well. \n\n### Poetry\n\nYou may also install KIPET with poetry:\n\n    poetry add kipet\n\n\n### GitHub\n\nAdditionally, KIPET may be installed directly from the repository (for example, if using poetry, simply install the desired branch (#branch) in the following manner):\n\n    poetry add git+https://github.com/salvadorgarciamunoz/kipet#master\n\nNaturally you can simply clone or download the repository if you wish.\n\n    cd <installation directory>\n    git clone https://github.com/salvadorgarciamunoz/kipet.git\n    cd kipet\n    python setup.py install\n\n\n### Examples and Tutorials\n\nAll of the example problems can be easily downloaded from the examples repository:\n\n    cd <example directory>\n    git clone https://github.com/kwmcbride/kipet_examples.git\n\n\nTo validate your installation, you can now run the test script included with the examples:\n\n    cd <example directory>\n    python run_examples.py\n\n<br>\n\n## License\n\nGPL-3\n\n\n## Authors\n\n    - Kevin McBride - Carnegie Mellon University\n    - Kuan-Han Lin - Carnegie Mellon University\n    - Christina Schenk - Basque Center for Applied Mathematics\n    - Michael Short - University of Surrey\n    - Jose Santiago Rodriguez - Purdue University\n    - David M. Thierry - Carnegie Mellon University\n    - Salvador García-Muñoz - Eli Lilly\n    - Lorenz T. Biegler - Carnegie Mellon University\n\n## Please cite\n<br>\n\n - C. Schenk, M. Short, J.S. Rodriguez, D. Thierry, L.T. Biegler, S. García-Muñoz, W. Chen (2020)\nIntroducing KIPET: A novel open-source software package for kinetic parameter estimation from experimental datasets including spectra, Computers & Chemical Engineering, 134, 106716. https://doi.org/10.1016/j.compchemeng.2019.106716\n\n - M. Short, L.T. Biegler, S. García-Muñoz, W. Chen (2020)\nEstimating variances and kinetic parameters from spectra across multiple datasets using KIPET, Chemometrics and Intelligent Laboratory Systems, https://doi.org/10.1016/j.chemolab.2020.104012\n\n - M. Short, C. Schenk, D. Thierry, J.S. Rodriguez, L.T. Biegler, S. García-Muñoz (2019)\nKIPET–An Open-Source Kinetic Parameter Estimation Toolkit, Computer Aided Chemical Engineering, 47, 299-304.\n\n\n\n\n\n\n',
    'author': 'Kevin McBride',
    'author_email': 'kevin.w.mcbride.86@gmail.com',
    'maintainer': 'Kevin McBride',
    'maintainer_email': 'kevin.w.mcbride.86@gmail.com',
    'url': 'https://github.com/kwmcbride/kipet',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
