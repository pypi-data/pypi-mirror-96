"""A parser for reading DLR BCEcmp Software SISRE output files

Example:
--------

    from midgard import parsers
    p = parsers.parse_file(parser_name='bcecmp_sisre', file_path='BCEcmp_GAL_FNAV_E1E5A_com_2018_032.OUT')
    data = p.as_dict()

Description:
------------

Reads data from files in the BCEcmp Software output file format. The BCEcmp Software is developed and used by DLR.

"""

# Standard library imports
from datetime import datetime
import itertools
import re
from typing import Any, Callable, Dict, Iterable, List

# Third party imports
import numpy as np

# Midgard imports
from midgard.dev import plugins
from midgard.parsers import ChainParser, ParserDef


@plugins.register
class BcecmpParser(ChainParser):
    """A parser for reading DLR BCEcmp Software output files.

    The following **data** are available after reading BCEcmp Software output file:

    | Key                   | Description                                                                          |
    |-----------------------|--------------------------------------------------------------------------------------|
    | age_min               | age of ephemeris in [min]                                                            |
    | clk_diff_with_dt_mean | Satellite clock correction difference corrected for average satellite clock offset   |
    |                       | difference for given GNSS and epoch in [m]                                           |
    | dalong_track          | Along-track orbit difference in [m]                                                  |
    | dcross_track          | Cross-track orbit difference in [m]                                                  |
    | dradial               | Radial orbit difference in [m]                                                       |
    | dradial_wul           | Worst-user-location (wul) SISRE?                                                     |
    | satellite             | Satellite PRN number together with GNSS identifier (e.g. G07)                        |
    | sisre                 | Signal-in-space range error [m]                                                      |
    | time                  | Observation time                                                                     |
    | used_iodc             | GPS: IODC (Clock issue of data indicates changes (set equal to IODE))                |
    |                       | QZSS: IODC                                                                           |
    | used_iode             | Ephemeris issue of data indicates changes to the broadcast ephemeris:                |
    |                       |   - GPS: Ephemeris issue of data (IODE), which is set equal to IODC                  |
    |                       |   - Galileo: Issue of Data of the NAV batch (IODnav)                                 |
    |                       |   - QZSS: Ephemeris issue of data (IODE)                                             |
    |                       |   - BeiDou: Age of Data Ephemeris (AODE)                                             |
    |                       |   - IRNSS: Issue of Data, Ephemeris and Clock (IODEC)                                |

    and **meta**-data:

    | Key                   | Description                                                                          |
    |-----------------------|--------------------------------------------------------------------------------------|
    | \__data_path__        | File path                                                                            |
    | \__parser_name__      | Parser name                                                                          |
    """

    #
    # PARSERS
    #
    def setup_parser(self) -> Iterable[ParserDef]:
        """Parsers defined for reading BCEcmp Software output file line by line.
        """

        #    Date       GPS time    PRN     R'[m]   A [m]   C [m]    T'[m]  dr_wul[m] sisrega[m]    IODE IODC age[min]
        # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8----+----9----+----0----+----1
        # 2018/02/01  00:00:00.000  E05    -0.108  -0.286   0.113   -0.241   -0.172    0.140       64   64      0.0
        # 2018/02/01  00:00:00.000  E07    -0.127   0.200   0.019    0.115   -0.167    0.241       64   64      0.0
        # 2018/02/01  00:00:00.000  E12     0.181  -0.232  -0.066    0.191    0.229    0.033       64   64      0.0
        data_parser = ParserDef(
            end_marker=lambda _l, _ln, _n: True,
            label=lambda line, _ln: not re.match("\d+/\d+/\d+", line),
            parser_def={
                False: {
                    "parser": self._parse_data,
                    "fields": {
                        "date": (0, 10),
                        "gps_time": (10, 24),
                        "satellite": (24, 29),
                        "dradial": (29, 39),
                        "dalong_track": (39, 47),
                        "dcross_track": (47, 55),
                        "clk_diff_with_dt_mean": (55, 64),
                        "dradial_wul": (64, 73),
                        "sisre": (73, 82),
                        "used_iode": (82, 91),
                        "used_iodc": (91, 96),
                        "age_min": (96, 105),
                    },
                }
            },
        )

        return itertools.chain(itertools.repeat(data_parser))

    #
    # DATA PARSERS
    #
    def _parse_data(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse BCEcmp Software output file entries to instance variable `data`.
        """
        # Parse date fields
        time = datetime.strptime(line["date"] + line["gps_time"], "%Y/%m/%d%H:%M:%S.%f")
        self.data.setdefault("time", list()).append(time)
        for f in ["date", "gps_time"]:
            del line[f]

        # Parse text fields
        self.data.setdefault("satellite", list()).append(line["satellite"])
        del line["satellite"]

        # Parse float fields
        for field, value in line.items():
            self.data.setdefault(field, list()).append(_float(value))

    #
    # SETUP CALCULATION
    #
    def setup_postprocessors(self) -> List[Callable[[], None]]:
        """List steps necessary for postprocessing
        """
        return [self._add_system_field]

    def _add_system_field(self) -> None:
        """Add system parameter to data
        """
        self.data["system"] = np.array(self.data["satellite"]).astype("U1")


# TODO: Maybe better to have this routine in a module.
def _float(value: str) -> float:
    """Convert string to float value

    Convert a string to a floating point number (including, e.g. -0.5960D-01). Whitespace or empty value is set to 0.0.

    Args:
        value: String value

    Returns:
        Float value
    """
    if value.isspace() or not value:
        return 0.0
    else:
        return float(value.replace("D", "e"))
