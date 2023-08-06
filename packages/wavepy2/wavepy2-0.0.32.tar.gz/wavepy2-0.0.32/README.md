# WavePy 2.0

Wavepy2 is a refactored version of [wavepy](https://github.com/APS-XSD-OPT-Group/wavepy) and [wavepytools](https://github.com/APS-XSD-OPT-Group/wavepytools).

Prerequisites: `xraylib 3.3.0` - see: https://github.com/tschoonj/xraylib/wiki/Installation-instructions

To install:               `python3 -m pip install wavepy2`
  
To show help:             `python3 -m wavepy2.tools --h`

To run a script:          `python3 -m wavepy2.tools <script id> <options>`
  
To show help of a script: `python -m wavepy2.tools <script id> --h`
  

Available scripts:
1) Imaging   - Single Grating Talbot, id: `img-sgt`
2) Coherence - Single Grating Z Scan, id: `coh-sgz`
3) Metrology - Fit Residual Lenses,   id: `met-frl`
