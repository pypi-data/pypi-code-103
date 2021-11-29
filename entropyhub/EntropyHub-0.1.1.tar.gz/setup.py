"""
EntropyHub - An open source toolkit for entropic time series analysis

  EntropyHub functions belong to one of five main classes/categories:
    Base Entropies             >>  e.g. Approximate Entropy (ApEn),
                                        Sample Entropy (SampEn)
    Cross Entropies            >>  e.g. Cross-Approximate Entropy (XApEn)
                                        Cross-Sample Entropy (XSampEn)
    Bidimensional Entropies    >>  e.g. Bidimensional Sample Entropy (SampEn2D)
                                        Bidimensional Fuzzy Entropy (FuzzEn2D)
    Multiscale Entropies       >>  e.g. Multiscale Sample Entropy (MSEn)
                                        Refined Multiscale Sample Entropy (rMSEn)
                                        Composite Multiscale Sample Entropy (cMSEn)
    Multiscale Cross Entropies >>  e.g. Multiscale Cross-Sample Entropy (XMSEn)
                                        Refined Multiscale Cross-Sample Entropy (rXMSEn)

_________________________________________________________________________
Base Entropies                                        |	Function Name	
______________________________________________________|__________________
Approximate Entropy                               	  |	ApEn
Sample Entropy                                		  |	SampEn
Fuzzy Entropy                                 		  |	FuzzEn
Kolmogorov Entropy                            		  |	K2En
Permutation Entropy                           		  |	PermEn
Conditional Entropy                           		  |	CondEn
Distribution Entropy                          		  |	DistEn
Spectral Entropy                              		  |	SpecEn
Dispersion Entropy                            		  |	DispEn
Symbolic Dynamic Entropy                          	  |	SyDyEn
Increment Entropy                                 	  |	IncrEn
Cosine Similarity Entropy                         	  |	CoSiEn
Phase Entropy                                         |	PhasEn
Slope Entropy                                      	  |	SlopEn
Bubble Entropy                                		  |	BubbEn
Gridded Distribution Entropy                          |	GridEn
Entropy of Entropy                            	      |	EnofEn
Attention Entropy                                     |	AttnEn

_________________________________________________________________________
Cross Entropies                                       |	Function Name
______________________________________________________|__________________
Cross Sample Entropy                                  |	XSampEn
Cross Approximate Entropy                             |	XApEn
Cross Fuzzy Entropy                                   |	XFuzzEn
Cross Permutation Entropy                             |	XPermEn
Cross Conditional Entropy                             |	XCondEn
Cross Distribution Entropy                            |	XDistEn
Cross Spectral Entropy                          	  |	XSpecEn
Cross Kolmogorov Entropy                              |	XK2En
	
_________________________________________________________________________
Bi-Dimensional Entropies                              |	Function Name
______________________________________________________|__________________
Bi-Dimensional Sample Entropy                         |	SampEn2D
Bi-Dimensional Fuzzy Entropy                          |	FuzzEn2D
Bi-Dimensional Distribution Entropy                   |	DistEn2D
Bi-Dimensional Dispersion Entropy                     |	DispEn2D
	
_________________________________________________________________________
Multiscale Entropy Functions                          | Function Name
______________________________________________________|__________________ 
Multiscale Entropy Object                             | MSobject
                                                      |
Multiscale Entropy                                    | MSEn
Composite/Refined-Composite Multiscale Entropy        | cMSEn
Refined Multiscale Entropy                            | rMSEn
Hierarchical Multiscale Entropy Object                | hMSEn

_________________________________________________________________________
Multiscale Entropies	MSEn                          |	Function Name
______________________________________________________|__________________
Multiscale Sample Entropy                             |	
Multiscale Approximate Entropy                        |	
Multiscale Fuzzy Entropy                              |	
Multiscale Permutation Entropy                        |	
Multiscale Dispersion Entropy                         |	
Multiscale Cosine Similarity Entropy                  |	
Multiscale Symblic Dynamic Entropy                    |	MSobject
Multiscale Conditional Entropy                        |	     +
Multiscale Entropy of Entropy                         | MSEn / cMSEn
Multiscale Gridded Distribution Entropy               |	rMSEn / hMSEn
Multiscale Slope Entropy                              |
Multiscale Phase Entropy                              |		
Multiscale Kolmogorov Entropy                         |	
Multiscale Distribution Entropy                       |		
Multiscale Bubble Entropy                             |	
Multiscale Increment Entropy                          |	
Multiscale Attention Entropy                          |	
	
_________________________________________________________________________
Multiscale Cross-Entropy Functions                    | Function Name
______________________________________________________|__________________
Multiscale Cross-Entropy Object                       |   MSobject
                                                      |
Multiscale Cross-Entropy                              |   XMSEn
Composite/Refined-Composite Multiscale Cross-Entropy  |   cXMSEn
Refined Multiscale Entropy                            |   rXMSEn
Hierarchical Multiscale Entropy Object                |   hXMSEn

_________________________________________________________________________
Multiscale Cross-Entropies                            |	Function Name
______________________________________________________|__________________
Multiscale Cross-Sample Entropy                       |	
Multiscale Cross-Approximate Entropy                  |	
Multiscale Cross-Fuzzy Entropy                        |	MSobject
Multiscale Cross-Permutation Entropy                  |	    +
Multiscale Cross-Distribution Entropy                 |	XMSEn / cXMSEn
Multiscale Cross-Kolmogorov Entropy                   | rXMSEn / hXMSEn
Multiscale Cross-Conditional Entropy                  |	


We kindly ask that if you use EntropyHub in your research, to please 
include the following citation with the appropriate version number,
as well as original articles upon which functions are derived:

Matthew W. Flood and Bernd Grimm (2021), 
"EntropyHub - An open source toolkit for entropic time series analysis"
PLoS ONE 16(11):e0259448, 
https://doi.org/10.1371/journal.pone.0259448

www.EntropyHub.xyz

© Copyright 2021 Matthew W. Flood, EntropyHub

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

For Terms of Use see https://github.com/MattWillFlood/EntropyHub
"""

from setuptools import setup #find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_desc = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='EntropyHub',  # Required
    version='0.1.1',  # Required
    description='An open-source toolkit for entropic time series analysis.',  # Optional
    long_description=long_desc,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)

    url='https://www.EntropyHub.xyz',  # Optional
    author='Matthew W. Flood',  # Optional
    author_email='info@entropyhub.xyz, help@entropyhub.xyz',  # Optional
    license = 'Apache 2.0',

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',        
        'Intended Audience :: Science/Research',        
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: Apache Software License',        
        'Natural Language :: English',        
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],

    keywords=('entropy, nonlinear, time series, statistics, physics, mathematics, signal processing,'
                'statistical physics, entropic, toolkit, research, multiscale, regularity, periodic,'
                'sample entropy, approximate entropy, fuzzy entropy, permutation entropy, uncertainty,'
                'dispersion entropy, kolmogorov, conditional entropy, composite, refined,'
                'randomness, random, signal analysis, nonlinearity, julia, matlab, open-source,'
                'refined-composite, hierarchical entropy, information theory, shannon entropy, complexity'),  # Optional

    
    packages = ['EntropyHub'], #find_packages(include ='EntropyHub*'),  # Required
    python_requires='>=3.6, <4',
    install_requires=['numpy', 'matplotlib', 'scipy', 'EMD-signal', 'requests'],  #'itertools', 'copy', #wheel?  Optional


    project_urls={  # Optional
        'Contact': 'https://www.entropyhub.xyz/#contact',
        'Examples': 'https://www.entropyhub.xyz/python/pyexamples.html',
        'Collaboration': 'https://www.researchgate.net/profile/Matthew-Flood-3',
        'Citation': 'https://doi.org/10.1371/journal.pone.0259448',
        'Bug Reports': 'https://github.com/MattWillFlood/EntropyHub/issues',
        #'Funding': 'https://donate.pypi.org',
        #'Say Thanks!': 'http://saythanks.io/to/example',
        'Source': 'https://www.EntropyHub.xyz',
        'Documentation': 'https://github.com/MattWillFlood/EntropyHub/blob/main/EntropyHub_Guide.pdf'
        
    },
)