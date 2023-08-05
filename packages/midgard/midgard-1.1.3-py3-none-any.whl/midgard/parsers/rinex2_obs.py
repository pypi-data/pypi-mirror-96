"""A parser for reading Rinex data

Example:
--------

    from midgard import parsers
    
    # Parse data
    parser = parsers.parse_file(parser_name="rinex2_obs", file_path=file_path)
    
    # Get Dataset with parsed data
    dset = parser.as_dataset()

Description:
------------

Reads data from files in the Rinex file format 2.11 (see :cite:`rinex2`).

"""

# Standard library imports
from datetime import timedelta
import dateutil.parser
import itertools
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union

# External library imports
import numpy as np

# Midgard imports
from midgard.data import dataset
from midgard.dev import plugins
from midgard.dev import log
from midgard.gnss.gnss import obstype_to_freq
from midgard.parsers import ChainParser, ParserDef
from midgard.math.constant import constant
from midgard.math.unit import Unit


SYSTEM_TIME_OFFSET_TO_GPS_TIME = dict(BDT=14, GAL=0, IRN=0, QZS=0)


@plugins.register
class Rinex2Parser(ChainParser):
    """A parser for reading RINEX observation file

    The parser reads GNSS observations in RINEX format 2.11 (see :cite:`rinex2`). The GNSS observations
    are sampled after sampling rate definition in configuration file.

    Attributes:
        convert_unit (Boolean):       Convert unit from carrier-phase and Doppler observation to meter. Exception:
                                      unit conversion for GLONASS observations is not implemented.
        data (Dict):                  The (observation) data read from file.
        data_available (Boolean):     Indicator of whether data are available.
        file_encoding (String):       Encoding of the datafile.
        file_path (Path):             Path to the datafile that will be read.
        meta (Dict):                  Metainformation read from file.
        parser_name (String):         Name of the parser (as needed to call parsers.parse_...).
        sampling_rate (Float):        Sampling rate in seconds.
        system (String):              GNSS identifier.
        time_scale (String):          Time scale, which is used to define the time scale of Dataset. GPS time scale is
                                      used. If another time scale is given e.g. BDT, then the time entries are 
                                      converted to GPS time scale. An exception is if GLONASS time scale is given, 
                                      then UTC is used as time scale. Hereby should be noted, the reported GLONASS time
                                      has the same hours as UTC and not UTC+3 h as the original GLONASS System Time in
                                      the RINEX file definition.
    """

    def __init__(
        self,
        *args: Tuple[Any],
        sampling_rate: Union[None, float] = None,
        convert_unit: bool = False,
        **kwargs: Dict[Any, Any],
    ) -> None:
        """Initialize Rinex2-parser

        Args:
            args:           Parameters without keyword.
            sampling_rate:  Sampling rate in seconds.
            kwargs:         Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.obstypes_all = list()
        self.time_scale = "gps"
        self.sampling_rate = sampling_rate
        self.convert_unit = convert_unit
        log.debug(f"Sampling rate for RINEX observations is {self.sampling_rate} second(s).")

    #
    # PARSERS
    #
    def setup_parser(self) -> Iterable[ParserDef]:
        """Parsers defined for reading RINEX observation file line by line.

           First the RINEX header information are read and afterwards the RINEX observation.
        """
        # Parser for RINEX header
        header_parser = ParserDef(
            end_marker=lambda line, _ln, _n: line[60:73] == "END OF HEADER",
            label=lambda line, _ln: line[60:].strip(),
            parser_def={
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #      2.11           OBSERVATION DATA    M (MIXED)           RINEX VERSION / TYPE
                "RINEX VERSION / TYPE": {
                    "parser": self._parse_rinex_version_type,
                    "fields": {"version": (0, 20), "file_type": (20, 21), "sat_sys": (40, 41)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # XXRINEXO V9.9       AIUB                24-MAR-01 14:43     PGM / RUN BY / DATE
                "PGM / RUN BY / DATE": {
                    "parser": self._parse_string,
                    "fields": {"program": (0, 20), "run_by": (20, 40), "file_created": (40, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # G = GPS R = GLONASS E = GALILEO S = GEO M = MIXED           COMMENT
                "COMMENT": {"parser": self._parse_comment, "fields": {"comment": (0, 60)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # A 9080                                                      MARKER NAME
                "MARKER NAME": {"parser": self._parse_string, "fields": {"marker_name": (0, 60)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # 9080.1.34                                                   MARKER NUMBER
                "MARKER NUMBER": {"parser": self._parse_string, "fields": {"marker_number": (0, 20)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # BILL SMITH          ABC INSTITUTE                           OBSERVER / AGENCY
                "OBSERVER / AGENCY": {
                    "parser": self._parse_string,
                    "fields": {"observer": (0, 20), "agency": (20, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # X1234A123           XX                  ZZZ                 REC # / TYPE / VERS
                "REC # / TYPE / VERS": {
                    "parser": self._parse_string,
                    "fields": {"receiver_number": (0, 20), "receiver_type": (20, 40), "receiver_version": (40, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # 234                 YY                                      ANT # / TYPE
                "ANT # / TYPE": {
                    "parser": self._parse_string,
                    "fields": {"antenna_number": (0, 20), "antenna_type": (20, 40)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #   4375274.       587466.      4589095.                      APPROX POSITION XYZ
                "APPROX POSITION XYZ": {
                    "parser": self._parse_approx_position,
                    "fields": {"pos_x": (0, 14), "pos_y": (14, 28), "pos_z": (28, 42)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #          .9030         .0000         .0000                  ANTENNA: DELTA H/E/N
                "ANTENNA: DELTA H/E/N": {
                    "parser": self._parse_float,
                    "fields": {"antenna_height": (0, 14), "antenna_east": (14, 28), "antenna_north": (28, 42)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #      1     1                                                WAVELENGTH FACT L1/2
                #      1     2     6   G14   G15   G16   G17   G18   G19      WAVELENGTH FACT L1/2
                "WAVELENGTH FACT L1/2": {
                    "parser": self._parse_wavelength_fact,
                    "fields": {
                        "l1_wave_fact": (0, 6),
                        "l2_wave_fact": (6, 12),
                        "num_satellite": (12, 18),
                        "prn_1": (21, 24),
                        "prn_2": (27, 30),
                        "prn_3": (33, 36),
                        "prn_4": (39, 42),
                        "prn_5": (45, 48),
                        "prn_6": (51, 54),
                        "prn_7": (57, 60),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     14    C1    C2    C5    P1    P2    L1    L2    L5    D1# / TYPES OF OBSERV
                #           D2    D5    S1    S2    S5                        # / TYPES OF OBSERV
                "# / TYPES OF OBSERV": {
                    "parser": self._parse_types_of_observ,
                    "fields": {
                        "num_obstypes": (0, 6),
                        "type_1": (6, 12),
                        "type_2": (12, 18),
                        "type_3": (18, 24),
                        "type_4": (24, 30),
                        "type_5": (30, 36),
                        "type_6": (36, 42),
                        "type_7": (42, 48),
                        "type_8": (48, 54),
                        "type_9": (54, 60),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     18.000                                                  INTERVAL
                "INTERVAL": {"parser": self._parse_float, "fields": {"interval": (0, 10)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #   2005     3    24    13    10   36.0000000                 TIME OF FIRST OBS
                "TIME OF FIRST OBS": {
                    "parser": self._parse_time_of_first_obs,
                    "fields": {
                        "year": (0, 6),
                        "month": (6, 12),
                        "day": (12, 18),
                        "hour": (18, 24),
                        "minute": (24, 30),
                        "second": (30, 43),
                        "time_sys": (48, 51),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #   2005     3    24    23    59   59.0000000                 TIME OF LAST OBS
                "TIME OF LAST OBS": {
                    "parser": self._parse_time_of_last_obs,
                    "fields": {
                        "year": (0, 6),
                        "month": (6, 12),
                        "day": (12, 18),
                        "hour": (18, 24),
                        "minute": (24, 30),
                        "second": (30, 43),
                        "time_sys": (48, 51),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #      0                                                      RCV CLOCK OFFS APPL
                "RCV CLOCK OFFS APPL": {"parser": self._parse_string, "fields": {"rcv_clk_offset_flag": (0, 6)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     13                                                      LEAP SECONDS
                "LEAP SECONDS": {"parser": self._parse_leap_seconds, "fields": {"leap_seconds": (0, 6)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     71                                                      # OF SATELLITES
                "# OF SATELLITES": {"parser": self._parse_integer, "fields": {"num_satellites": (0, 6)}},
                # TODO: 'PRN / # OF OBS'
            },
        )

        # Parser for RINEX observation blocks

        # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
        #  16  3  1  0  0  0.0000000  0 19G07G27G20G21G26G15G10G16G08G18G30R06  .000000000
        #                                 R22R21R04R13R20R11R05
        #      1     2     2   G 9   G12                              WAVELENGTH FACT L1/2
        #   *** WAVELENGTH FACTOR CHANGED FOR 2 SATELLITES ***        COMMENT
        #   23522570.266    23522573.871            .000    23522570.500    23522573.969
        #  123611978.15417  96321063.91253          .000         932.031         726.258
        obs_parser = ParserDef(
            end_marker=lambda _l, _ln, next_line: (next_line[2:3].isdigit() and next_line[3:4].isspace()),
            label=lambda line, _ln: (
                (line[10:11] == "." or line[0:16].isspace())  # Accepting of value or blank entry
                and not line[32:33].isalpha()  # Continuation of satellite list
                and not (
                    line[34:35].isnumeric() and line[35:36].isspace()
                )  # Continuation of satellite list with blank satellite system identifier (GPS only)
                and not line[60:61].isalpha()
            ),  # Comment line
            parser_def={
                False: {
                    "parser": self._parse_observation_epoch,
                    "strip": "\n",  # Remove only newline '\n' leading and trailing characters from line.
                    "fields": {
                        "year": (0, 3),
                        "month": (3, 6),
                        "day": (6, 9),
                        "hour": (9, 12),
                        "minute": (12, 15),
                        "second": (15, 26),
                        "epoch_flag": (26, 29),
                        "num_sat": (29, 32),
                        "sat_list": (32, 68),
                        "rcv_clk_offset": (68, 80),
                    },
                },
                True: {
                    "parser": self._parse_observation,
                    "strip": "\n",  # Remove only newline '\n' leading and trailing characters from line.
                    "fields": {
                        "obs_1": (0, 16),
                        "obs_2": (16, 32),
                        "obs_3": (32, 48),
                        "obs_4": (48, 64),
                        "obs_5": (64, 80),
                    },
                },
            },
        )

        return itertools.chain([header_parser], itertools.repeat(obs_parser))

    #
    # HEADER PARSERS
    #
    def _parse_approx_position(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse station coordinates defined in RINEX header to instance variable
          'data'.
        """
        pos = np.array((float(line["pos_x"]), float(line["pos_y"]), float(line["pos_z"])))
        self.data["pos"] = pos
        self._parse_float(line, _)

    def _parse_comment(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse comment lines in RINEX header to instance variable `meta['comment']`.
        """
        self.meta.setdefault("comment", list()).append(line["comment"])

    def _parse_float(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse float entries of RINEX header to instance variable `meta`.
        """
        self.meta.update({k: float(v) for k, v in line.items()})

    def _parse_integer(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse integer entries of RINEX header to instance variable `meta`.
        """
        self.meta.update({k: int(v) for k, v in line.items()})

    def _parse_leap_seconds(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `LEAP SECONDS` to instance variable `meta`.

            self.meta['leap_seconds'] = { 'leap_seconds': <value>' }

            NOTE: Entries 'future_past_leap_seconds', 'week', 'week_day' and 'time_sys' are not given in RINEX version
                  2.11.
        """
        for field in line:
            self.meta.setdefault("leap_seconds", {}).update({field: line[field]})

    def _parse_rinex_version_type(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `RINEX VERSION / TYPE` to instance variable `meta`.
        """
        self.meta.update({k: v for k, v in line.items()})

        # A blank satellite system identifier indicates GPS ('G').
        if not self.meta["sat_sys"]:
            self.meta["sat_sys"] = "G"

    def _parse_string(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse string entries of RINEX header to instance variable `meta`.
        """
        self.meta.update({k: v for k, v in line.items()})

    def _parse_time_of_first_obs(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse time of first observation given in RINEX header to instance variable `meta`.
        """
        if line["time_sys"] != "GPS":
            log.fatal(f"Time system {line['time_sys']} is not handled so far in Where")

        if line["time_sys"]:
            self.meta["time_sys"] = line["time_sys"]

        if line["year"]:
            self.meta["time_first_obs"] = (
                "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:010.7f}"
                "".format(
                    year=int(line["year"]),
                    month=int(line["month"]),
                    day=int(line["day"]),
                    hour=int(line["hour"]),
                    minute=int(line["minute"]),
                    second=float(line["second"]),
                )
            )

    def _parse_time_of_last_obs(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse time of last observation given in RINEX header to instance variable `meta`.
        """
        if line["time_sys"] != "GPS":
            log.fatal(f"Time system {line['time_sys']} is not handled so far in Where")

        if line["time_sys"]:
            self.meta["time_sys"] = line["time_sys"]

        if line["year"]:
            self.meta["time_last_obs"] = (
                "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:010.7f}"
                "".format(
                    year=int(line["year"]),
                    month=int(line["month"]),
                    day=int(line["day"]),
                    hour=int(line["hour"]),
                    minute=int(line["minute"]),
                    second=float(line["second"]),
                )
            )

    def _parse_types_of_observ(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse observation types given in RINEX header to instance variable `meta` and `data`.
        """
        # TODO: Should RINEX v2 observation types be converted to RINEX v3 convention?
        #      A unique conversion from RINEX2 to RINEX3 is not possible, also if known what kind of observations
        #      a receiver tracks. Especially the carrier phase observations are derived based on one of the code
        #      observations. The RINEX2 format provides not the information about to which code the carrier phase
        #      observations are related (e.g. C1C, C1W, C1X, C1L, ...). In addition each station provider can configure
        #      their GNSS receivers differently. So in principle for each station the configuration and the resulting
        #      observations types has to be known so that we can do at least a unique conversion for code observations.
        #      How relevant is it, if we would use e.g. L1C instead L1X or C1C instead of C1X?
        #
        # Following list is based on gLAB routine dataHandling.c (measstr2meastype):
        #      v2    v3 (gLAB)  v3 (Where)
        # __________________________________
        #      C1    C1C        C1C
        #      P1    C1P        C1W
        #      L1    L1P        L1
        #      D1    D1P        D1
        #      S1    S1P        S1

        #      C2    C2C        C2
        #      P2    C2P        C2W
        #      L2    L2P        L2
        #      D2    D2P        D2
        #      S2    S2P        S2

        #      C5    C5X
        #      L5    L5X
        #      D5    D5X
        #      S5    S5X

        #      C6    C6X
        #      L6    L6X
        #      D6    D6X
        #      S6    S6X

        #      C7    C7X
        #      L7    L7X
        #      D7    D7X
        #      S7    S7X

        #      C8    C8X
        #      L8    L8X
        #      D8    D8X
        #      S8    S8X

        if line["num_obstypes"]:
            self.meta["num_obstypes"] = int(line["num_obstypes"])
            self.meta["obstypes"] = list()

        self.data.setdefault("obs", {})
        self.data.setdefault("cycle_slip", {})
        self.data.setdefault("signal_strength", {})

        for field in sorted([f for f in line if f.startswith("type_")]):
            if line[field]:
                self.meta["obstypes"].append(line[field])
                self.data["obs"][line[field]] = list()
                self.data["cycle_slip"][line[field]] = list()
                self.data["signal_strength"][line[field]] = list()

    def _parse_wavelength_fact(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse wavelength factors for L1 and L2 (GPS) to instance variable `meta`.
        """
        if line["num_satellite"]:
            self.meta["l1_wave_fact_prn"] = line["l1_wave_fact"]
            self.meta["l2_wave_fact_prn"] = line["l2_wave_fact"]
            self.meta["wave_fact_prn"] = list()
        else:
            self.meta["l1_wave_fact_default"] = line["l1_wave_fact"]
            self.meta["l2_wave_fact_default"] = line["l2_wave_fact"]

        for field in sorted([f for f in line if f.startswith("prn_")]):
            if line[field]:
                self.meta["wave_fact_prn"].append(line[field])

    #
    # OBSERVATION PARSERS
    #
    def _parse_observation_epoch(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation epoch information of RINEX observation record

        Only the last 2-digits of the year is given in the observation epoch, therefore it is necessary to get the
        complete 4-digit year based on the `TIME OF FIRST OBS` and `TIME OF LAST OBS` the RINEX header entries.

        In addition the RINEX observation are decimated based on the given sampling rate.
        """
        # Reject empty lines
        line["year"] = line["year"].strip()
        if (not line["year"].isnumeric()) and (not line["sat_list"]):
            return

        # Reject comment lines
        if line["sat_list"][28:29].isalpha():
            return

        # Read observation epoch entry
        if line["year"]:

            # Get correct 4-digit year (in observation epoch only 2-digit year is given)
            first_obs_year = self.meta["time_first_obs"][0:4]
            year = int(first_obs_year[0:2] + line["year"].zfill(2))

            # Check if 'year' is unique in the complete RINEX file
            if "time_last_obs" in self.meta:
                last_obs_year = self.meta["time_last_obs"][0:4]

                if first_obs_year != last_obs_year:
                    log.fatal(
                        f"Different year for first and last observation is given in RINEX "
                        f"({first_obs_year} and {last_obs_year}). RINEX routine has to be improved"
                    )

            cache["sat_list"] = list()
            cache["obs_time"] = "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:010.7f}" "".format(
                year=year,
                month=int(line["month"]),
                day=int(line["day"]),
                hour=int(line["hour"]),
                minute=int(line["minute"]),
                second=float(line["second"]),
            )
            cache["obs_sec"] = (
                int(line["hour"]) * Unit.hour2second + int(line["minute"]) * Unit.minute2second + float(line["second"])
            )
            cache["epoch_flag"] = int(line["epoch_flag"])
            cache["rcv_clk_offset"] = _float(line["rcv_clk_offset"])

            # Decimate RINEX observation defined by sampling rate [seconds]
            if self.sampling_rate:
                if cache["obs_sec"] % self.sampling_rate != 0:
                    cache["obs_sec"] = None  # Ignore epoch

            cache["num_sat"] = int(line["num_sat"])

        if (line["epoch_flag"].strip() != "0") and line["epoch_flag"].strip():
            log.fatal(
                f"Epoch {cache['obs_time']} is not ok, which is indicated by epoch flag {line['epoch_flag']}.\n"
                f"TODO: How should it be handled in Where?"
            )  # TODO: Handle flagged epochs

        # Generate satellite list for given epoch
        for i in range(0, len(line["sat_list"]), 3):
            sat = line["sat_list"][i : i + 3].rstrip()
            if sat:
                sat = sat[0].replace(" ", "G") + sat[1].replace(" ", "0") + sat[2]  # Blank satellite system
                cache["sat_list"].append(sat)  # identifier indicates GPS ('G')

        cache["len_sat_list"] = len(cache["sat_list"])

    def _parse_observation(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation record of RINEX file
        """
        # Ignore epochs based on sampling rate
        sec = cache["obs_sec"]
        if sec is None:
            return

        if cache["num_sat"] != cache["len_sat_list"]:
            log.fatal(
                f"Number of satellites ({cache['num_sat']}) does not agree with number of satellites "
                f"in satellite PRN list ({cache['len_sat_list']}) in observation epoch {cache['obs_time']}"
            )

        # Read line with maximal 5 observations
        for field in sorted([f for f in line if f.startswith("obs_")]):

            # Fit length of observation (should always be 16 characters long)
            #
            # NOTE: This is necessary, because missing observations are written as 0.0 or BLANK in RINEX format and loss
            #       of lock indicator (LLI) and signal strength can be blank. In this case the length of observation
            #       field is fitted to 16 characters as defined in the RINEX 2.11 format description
            #
            #       Each observation type is saved in a Dataset field. The observation type fields have the same length
            #       to be consistent with the time, system or satellite Dataset field. The problem is that some
            #       observation types are not observed for a certain satellite system, but these observation are
            #       included with zero values in the observation type field.
            line[field] = line[field].ljust(16)

            cache.setdefault("obs_values", list()).append(_float(line[field][0:14]))
            cache.setdefault("cycle_slip", list()).append(_float(line[field][14:15]))
            cache.setdefault("signal_strength", list()).append(_float(line[field][15:16]))

        # Save all observation type entries for given satellite (all observation for a given epoch and satellite are
        # read)
        if len(cache["obs_values"]) >= self.meta["num_obstypes"]:

            sat = cache["sat_list"].pop(0)
            sys = sat[0]
            sat_num = int(sat[1:])
            for obs_type, obs, cycle_slip, signal_strength in zip(
                self.meta["obstypes"], cache["obs_values"], cache["cycle_slip"], cache["signal_strength"]
            ):
                self.data["obs"][obs_type].append(obs)
                self.data["cycle_slip"][obs_type].append(cycle_slip)
                self.data["signal_strength"][obs_type].append(signal_strength)
            del cache["obs_values"]
            del cache["cycle_slip"]
            del cache["signal_strength"]

            self.data.setdefault("time", list()).append(cache["obs_time"])
            self.data.setdefault("epoch_flag", list()).append(cache["epoch_flag"])
            self.data.setdefault("rcv_clk_offset", list()).append(cache["rcv_clk_offset"])

            obs = {
                "station": self.meta["marker_name"].lower(),  # vars['station'],
                "site_id": self.meta["marker_name"].upper(),
                "system": sys,
                "satellite": sat,
                "satnum": sat_num,
            }
            for field, value in obs.items():
                self.data.setdefault("text", dict()).setdefault(field, list()).append(value)

    #
    # SETUP POSTPROCESSORS
    #
    def setup_postprocessors(self) -> List[Callable[[], None]]:
        """List steps necessary for postprocessing
        """
        return [
            self._remove_empty_obstype_fields,
            self._get_obstypes_dict,
            self._time_system_correction,
            self._unit_conversion,
        ]

    def _remove_empty_obstype_fields(self) -> None:
        """Remove empty observation type data fields.

        The observation types given in RINEX header (# / TYPES OF OBSERV) define the key entries initialized in the
        data dictionaries `obs`, `cycle_slip` and `signal_strength`. It can happen, that no observations are available
        for observation types defined in the RINEX header. Empty observation type entries are deleted in this routine.
        """
        del_obs_type = []
        for obs_type, obs in self.data["obs"].items():
            if not obs or np.all(np.isnan(obs)):
                del_obs_type.append(obs_type)

        for obs_type in del_obs_type:
            del self.data["obs"][obs_type]
            del self.data["cycle_slip"][obs_type]
            del self.data["signal_strength"][obs_type]

            self.meta["obstypes"].remove(obs_type)

    def _get_obstypes_dict(self) -> None:
        """Generate GNSS dependent observation type dictionary

        The observation type information in the RINEX header is not related to the GNSS as it is the case for RINEX 3.
        Therefore the observation given for each observation type has to be checked, if they are tracked from a certain
        GNSS.

        Final observation type dictionary looks like:
            self.meta['obstypes'] = { <sat_sys>: [<ordered list with given observation types>]}
        """
        obstypes = dict()

        # Loop over GNSS
        for sys in set(self.data["text"]["system"]):
            idx = np.array(self.data["text"]["system"]) == sys

            # Loop over all observation types
            for obs_type in self.meta["obstypes"]:

                # Check if observation are given for the observation type (Note: Missing observations can be
                # indicated via 0.0 or via blank entry.)
                obs = np.array(self.data["obs"][obs_type])[idx]
                if len(obs) > 0 and not np.all(obs == 0.0):
                    obstypes.setdefault(sys, list()).append(obs_type)

        # Overwrite RINEX header observation type information with GNSS dependent information
        self.meta["obstypes"] = obstypes
        del self.meta["num_obstypes"]  # Not needed anymore.

    def _time_system_correction(self) -> None:
        """Apply correction to given time system for getting GPS or UTC time scale

        Following relationship are given between GNSS time scale (either BeiDou, Galileo, IRNSS or QZSS)
        :math:`t_{GNSS}` and GPS time scale :math:`t_{GPS}` (see Section 2.1.4 in :cite:`teunissen2017`):
        .. math::
              t_{GPS}  = t_{GNSS} + \Delta t

        The time offset :math:`\Delta t` is 0 s for Galileo, IRNSS and QZSS and for BeiDou 14 s. All these time scales
        are related to the International Atomic Time (TAI) by a certain time offset. An exception is the GLONASS time
        scale, which is related to UTC:
        .. math::
              t_{UTC}  = t_{GLONASS} - 3h

        Note, that in the RINEX format (see section 8.2 in :cite:`rinex2`) GLONASS time has the same hours as UTC and
        not UTC + 3h as the original GLONASS system time, which is given in the Moscow time zone instead of Greenwich.

        In this routine the given observation time (epoch) will be transformed to GPS time scale for BeiDou, Galileo,
        QZSS and IRNSS and to UTC time scale for GLONASS.
        """
        system = self.meta["time_sys"]
        valid_time_systems = ["BDT", "GAL", "GPS", "GLO", "IRN", "QZS"]

        if system not in valid_time_systems:
            log.fatal(
                f"Time system {system!r} in file {self.file_path} is not handled in Where. "
                f"The following time systems can be used: {', '.join(valid_time_systems)}"
            )

        # Convert observation time entries of BeiDou to GPS time scale by adding system time offset
        if system == "BDT":
            self.data["time"] = [
                dateutil.parser.parse(t) + timedelta(seconds=SYSTEM_TIME_OFFSET_TO_GPS_TIME.get(system, 0))
                for t in self.data["time"]
            ]

        # Change time scale to UTC for GLONASS
        elif system == "GLO":
            self.time_scale = "utc"

    def _unit_conversion(self) -> None:
        """Carrier-phase and Doppler observations are converted to meter
        
        Carrier-phase observations are given in cycles and Doppler observation in Hertz in RINEX observation file. 
        Exception: unit conversion for GLONASS observations is not implemented.
        """
        if self.convert_unit:

            for sys in set(self.data["text"]["system"]):
                if sys == "R":  # Frequency handling for GLONASS satellites is not implemented.
                    continue

                idx = sys == np.array(self.data["text"]["system"])

                for obstype in self.meta["obstypes"][sys]:
                    
                    if not obstype[0] in ["L", "D"]:  # Skip pseudorange and SNR observations
                        continue
                    log.debug(f"Conversion from observation type {obstype} (for GNSS: '{sys}') to meter.")
                    self.data["obs"][obstype] = np.array(self.data["obs"][obstype])
                    self.data["obs"][obstype][idx] = (
                        constant.c / obstype_to_freq(sys, obstype) * self.data["obs"][obstype][idx]
                    )

    # def pseudorange_system_correction(self):
    #    """Apply correction to pseudorange observations
    #
    #    See section 8.1.2 in :cite:`rinex2`.
    #    TODO: Is it necessary to correct the pseudorange observation depending on used time system?
    #    """

    #
    # WRITE DATA
    #
    def as_dataset(self) -> "Dataset":
        """Store GNSS data in a dataset

        Returns:
            Midgard Dataset where GNSS observation are stored with following fields:

       |  Field               | Type              | Description                                                           |
       |----------------------|-------------------|-----------------------------------------------------------------------|
       | <observation type>   | numpy.ndarray     | GNSS observation type data (e.g. C1, P2, L1, L2, ...) given           |
       |                      |                   | in meters. Only observation types are kept, which are defined in      |
       |                      |                   | configuration file. Observation types are rejected, which include     |
       |                      |                   | only blank or 0.0 entries.                                            |
       | epoch_flag           | numpy.ndarray     | Epoch flag                                                            |
       | rcv_clk_offset       | numpy.ndarray     | Receiver clock offset in seconds given for each epoch                 |
       | satellite            | numpy.ndarray     | Satellite PRN number together with GNSS system identifier             |
       |                      |                   | (e.g. G07). Only satellites are kept, which are defined in            |
       |                      |                   | configuration file.                                                   |
       | satnum               | numpy.ndarray     | Satellite PRN number (e.g. 07). Only satellites are kept, which are   |
       |                      |                   | defined in configuration file.                                        |
       | site_pos             | PositionTable     | PositionTable object with given station coordinates (read from        |
       |                      |                   | RINEX header)                                                         |
       | station              | numpy.ndarray     | Station name list                                                     |
       | system               | numpy.ndarray     | GNSS system identifier. Only satellite system are kept, which are     |
       |                      |                   | defined in configuration file.                                        |
       | time                 | TimeTable         | Observation time given as TimeTable object                            |

            and following Dataset `meta` data:

       |  Entry              | Type  | Description                                                                        |
       |---------------------|-------|------------------------------------------------------------------------------------|
       | agency              | str   | Name of agency from observer                                                       |
       | antenna_east        | float | East component of vector between marker and antenna reference point in meters      |
       | antenna_height      | float | Height component of vector between marker and antenna reference point in meters    |
       | antenna_north       | float | North component of vector between marker and antenna reference point in meters     |
       | antenna_number      | str   | Antenna serial number                                                              |
       | antenna_type        | str   | Antenna type                                                                       |
       | comment             | list  | List with RINEX header comment lines                                               |
       | file_created        | str   | Date and time of file creation                                                     |
       | file_type           | str   | File type (e.g. 'O' for observation data)                                          |
       | interval            | float | Observation interval in seconds                                                    |
       | l1_wave_fact_default| str   | Default wavelength factors for L1 (GPS only)                                       |
       | l1_wave_fact_prn    | str   | Wavelength factors for L1 (GPS only) valid for a list of satellite PRNs (see       |
       |                     |       | wave_fact_prn)                                                                     |
       | l2_wave_fact_default| str   | Default wavelength factors for L2 (GPS only)                                       |
       | l2_wave_fact_prn    | str   | Wavelength factors for L2 (GPS only) valid for a list of satellite PRNs (see       |
       |                     |       | wave_fact_prn)                                                                     |
       | leap_seconds        | dict  | Dictionary with information related to leap seconds                                |
       | marker_name         | str   | Name of antenna marker                                                             |
       | marker_number       | str   | Number of antenna marker                                                           |
       | num_satellites      | int   | Number of satellites, for which observations are stored in the RINEX file          |
       | observer            | str   | Name of observer                                                                   |
       | obstypes            | dict  | Observation types given for each GNSS, whereby observation types and GNSS are      |
       |                     |       | rejected, which are empty (blank or zero entries).                                 |
       | program             | str   | Name of program creating current file                                              |
       | rcv_clk_offset_flag | str   | Flag (1=yes, 0=no) indicating if realtime-derived receiver clock offset is         |
       |                     |       | applied for epoch, code, and phase                                                 |
       | receiver_number     | str   | Receiver serial number                                                             |
       | receiver_type       | str   | Receiver type                                                                      |
       | receiver_version    | str   | Receiver firmware version                                                          |
       | run_by              | str   | Name of agency creating current file                                               |
       | sat_sys             | str   | Satellite system given in observation file (G, R, E, S or M)                       |
       | time_first_obs      | str   | Time of first observation record                                                   |
       | time_last_obs       | str   | Time of last observation record                                                    |
       | time_sys            | str   | Time system used for GNSS observations (GPS, GLO or GAL)                           |
       | version             | str   | Format version                                                                     |
       | wave_fact_prn       | list  | List of satellite PRNs for which the wavelength factors l1_wave_fact_prn and       |
       |                     |       |  l2_wave_fact_prn are valid                                                        |
        """

        # Time
        # TODO: Handling of different time systems needed!!!
        dset = dataset.Dataset(num_obs=len(self.data["time"]))

        # TODO workaround: "isot" does not work for initialization of time field (only 5 decimals for seconds are
        #                  allowed). Therefore self.data["time"] is converted to datetime object.
        from datetime import datetime, timedelta

        date = []
        millisec = []
        for v in self.data["time"]:
            val, val2 = v.split(".")
            date.append(datetime.strptime(val, "%Y-%m-%dT%H:%M:%S"))
            millisec.append(timedelta(milliseconds=int(val2)))
        dset.add_time("time", val=date, val2=millisec, scale=self.time_scale, fmt="datetime")
        dset.add_float("epoch_flag", val=np.array(self.data["epoch_flag"]))
        dset.add_float("rcv_clk_offset", val=np.array(self.data["rcv_clk_offset"]))

        dset.meta.update(self.meta)

        for field, value in self.data["text"].items():
            dset.add_text(field, val=value)

        # Observations
        for obs_type in self.data["obs"]:
            dset.add_float(f"obs.{obs_type}", val=np.array(self.data["obs"][obs_type]), unit="meter")
            dset.add_float(f"lli.{obs_type}", val=np.array(self.data["cycle_slip"][obs_type]))
            dset.add_float(f"snr.{obs_type}", val=np.array(self.data["signal_strength"][obs_type]))

        # Positions
        dset.add_position(
            "site_pos", time=dset.time, system="trs", val=np.repeat(self.data["pos"][None, :], dset.num_obs, axis=0)
        )

        return dset


def _float(value: str) -> float:
    """Convert string to float value

    Whitespace, empty or zero value is set to NaN.

    Args:
        value: String value

    Returns:
        Float value
    """
    if value.isspace() or not value or float(value) == 0.0:
        return float("nan")
    else:
        return float(value)
