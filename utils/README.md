## Set of tools to handle LSST simulations

#### `serialize_lsst_sn_sims.py`

Takes as input a directory containing a run of simulations (e.g. `LSST_DDF_MODEL45`) and returns a compressed dictionary (`LSST_DDF_MODEL45.pkl` file) of supernovae data index by their ID. 
Such file can then be placed in the `data` directory of this RAMP to be processed just as the DES data.

##### Usage: 
```bash
python serialize_lsst_sn_sims.py <LSST_sim_dir>
python serialize_lsst_sn_sims.py <LSST_sim_dir1> <LSST_sim_dir2>
python serialize_lsst_sn_sims.py <LSST_sim_dir*> 
python serialize_lsst_sn_sims.py --help  # for help
```

##### Comment:
Python3 only

