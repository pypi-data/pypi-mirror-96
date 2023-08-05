This is an abstract bundle of lite tools, follow next to install detail tools, and use `nxp_lite_tools` command to find the link of this page.

**1. NXP power performance data submitter**

Install:

    $ pip install -UI nxp_lite_tools[pp]

Usage:

    $ nxp_pp_submit -h
    usage: nxp_pp_submit [-h] -c CONFIG -r RESULT [-d]

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            release config
      -r RESULT, --result RESULT
                            result file
      -d, --debug           mode

Desc:

    -c CONFIG: put the path of config.ini
    -r RESULT: if result file specified, submit this single result
               if result folder specified, iterate all .json and .csv in the folder, then submit all results
    -d       : set this flag if submit results to staging server
    
**2. NXP lf history data submitter**

[TODO]

**3. NXP NPI dashboard data submitter**

[TODO]