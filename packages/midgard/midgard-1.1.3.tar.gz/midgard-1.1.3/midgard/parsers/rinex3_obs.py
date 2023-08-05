"""A parser for reading RINEX format 3.03 data

Example:
--------

    from midgard import parsers
    
    # Parse data
    parser = parsers.parse_file(parser_name="rinex3_obs", file_path=file_path)
      
    # Get Dataset with parsed data
    dset = parser.as_dataset()

Description:
------------

Reads data from files in the RINEX file format version 3.03 (see :cite:`rinex3`).


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
class Rinex3Parser(ChainParser):
    """A parser for reading RINEX observation file

    The parser reads GNSS observations in RINEX format 3.03 (see :cite:`rinex3`). The GNSS observations
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
        time_scale (String):          Time scale, which is used to define the time scale of Dataset. GPS time scale is
                                      used. If another time scale is given e.g. BDT, then the time entries are 
                                      converted to GPS time scale. An exception is if GLONASS time scale is given, 
                                      then UTC is used as time scale. Hereby should be noted, the reported GLONASS time
                                      has the same hours as UTC and not UTC+3 h as the original GLONASS System Time in
                                      the RINEX file definition.
        system (String):              GNSS identifier.
    """

    def __init__(
        self,
        *args: Tuple[Any],
        sampling_rate: Union[None, float] = None,
        convert_unit: bool = False,
        **kwargs: Dict[Any, Any],
    ) -> None:
        """Initialize Rinex3-parser
        
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
                #      3.02           OBSERVATION DATA    M (MIXED)           RINEX VERSION / TYPE
                "RINEX VERSION / TYPE": {
                    "parser": self._parse_string,
                    "fields": {"version": (0, 20), "file_type": (20, 21), "sat_sys": (40, 41)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # MAKERINEX 2.0.20023 BKG/GOWETTZELL      2016-03-02 00:20    PGM / RUN BY / DATE
                "PGM / RUN BY / DATE": {
                    "parser": self._parse_string,
                    "fields": {"program": (0, 20), "run_by": (20, 40), "file_created": (40, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # G = GPS R = GLONASS E = GALILEO S = GEO M = MIXED           COMMENT
                "COMMENT": {"parser": self._parse_comment, "fields": {"comment": (0, 60)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # stas                                                        MARKER NAME
                "MARKER NAME": {"parser": self._parse_string, "fields": {"marker_name": (0, 60)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # 66008M005                                                   MARKER NUMBER
                "MARKER NUMBER": {"parser": self._parse_string, "fields": {"marker_number": (0, 20)}},
                "MARKER TYPE": {"parser": self._parse_string, "fields": {"marker_type": (0, 20)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # SATREF              Norwegian Mapping Authority             OBSERVER / AGENCY
                "OBSERVER / AGENCY": {
                    "parser": self._parse_string,
                    "fields": {"observer": (0, 20), "agency": (20, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # 3008040             SEPT POLARX4        2.9.0               REC # / TYPE / VERS
                "REC # / TYPE / VERS": {
                    "parser": self._parse_string,
                    "fields": {"receiver_number": (0, 20), "receiver_type": (20, 40), "receiver_version": (40, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # CR620012101         ASH701945C_M    SCIS                    ANT # / TYPE
                "ANT # / TYPE": {
                    "parser": self._parse_string,
                    "fields": {"antenna_number": (0, 20), "antenna_type": (20, 40)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #   3275756.7623   321111.1395  5445046.6477                  APPROX POSITION XYZ
                "APPROX POSITION XYZ": {
                    "parser": self._parse_approx_position,
                    "fields": {"pos_x": (0, 14), "pos_y": (14, 28), "pos_z": (28, 42)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #         0.0000        0.0000        0.0000                  ANTENNA: DELTA H/E/N
                "ANTENNA: DELTA H/E/N": {
                    "parser": self._parse_float,
                    "fields": {"antenna_height": (0, 14), "antenna_east": (14, 28), "antenna_north": (28, 42)},
                },
                "ANTENNA: DELTA X/Y/Z": {
                    "parser": self._parse_float,
                    "fields": {"ant_vehicle_x": (0, 14), "ant_vehicle_y": (14, 28), "ant_vehicle_z": (28, 42)},
                },
                # TODO: 'ANTENNA:PHASECENTER'
                # TODO: 'ANTENNA:B.SIGHT XYZ'
                # TODO: 'ANTENNA:ZERODIR AZI'
                # TODO: 'ANTENNA:ZERODIR XYZ'
                # TODO: 'CENTER OF MASS: XYZ'
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # G   26 C1C C1P L1C L1P D1C D1P S1C S1P C2P C2W C2S C2L C2X  SYS / # / OBS TYPES
                #        L2P L2W L2S L2L L2X D2P D2W D2S D2L D2X S2P S2W S2S  SYS / # / OBS TYPES
                # R   16 C1C C1P L1C L1P D1C D1P S1C S1P C2C C2P L2C L2P D2C  SYS / # / OBS TYPES
                #        D2P S2C S2P                                          SYS / # / OBS TYPES
                "SYS / # / OBS TYPES": {
                    "parser": self._parse_sys_obs_types,
                    "fields": {
                        "satellite_sys": (0, 1),
                        "num_obstypes": (3, 6),
                        "type_01": (7, 10),
                        "type_02": (11, 14),
                        "type_03": (15, 18),
                        "type_04": (19, 22),
                        "type_05": (23, 26),
                        "type_06": (27, 30),
                        "type_07": (31, 34),
                        "type_08": (35, 38),
                        "type_09": (39, 42),
                        "type_10": (43, 46),
                        "type_11": (47, 50),
                        "type_12": (51, 54),
                        "type_13": (55, 58),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # DBHZ                                                        SIGNAL STRENGTH UNIT
                "SIGNAL STRENGTH UNIT": {"parser": self._parse_string, "fields": {"signal_strength_unit": (0, 20)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     1.000                                                  INTERVAL
                "INTERVAL": {"parser": self._parse_float, "fields": {"interval": (0, 10)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #  2016    03    01    00    00   00.0000000     GPS         TIME OF FIRST OBS
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
                #   2016    03    01    23    59   59.0000000     GPS         TIME OF LAST OBS
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
                # G APPL_DCB          xyz.uvw.abc//pub/dcb_gps.dat            SYS / DCBS APPLIED
                "SYS / DCBS APPLIED": {
                    "parser": self._parse_sys_dcbs_applied,
                    "fields": {"sat_sys": (0, 1), "program": (2, 19), "source": (20, 60)},
                },
                "SYS / PCVS APPLIED": {
                    "parser": self._parse_sys_pcvs_applied,
                    "fields": {"sat_sys": (0, 1), "program": (2, 19), "source": (20, 60)},
                },
                "SYS / SCALE FACTOR": {
                    "parser": self._parse_scale_factor,  # TODO: not implemented
                    "fields": {"sat_sys": (0, 1), "factor": (2, 6), "num_obstypes": (8, 10)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # G L1C  0.00000  12 G01 G02 G03 G04 G05 G06 G07 G08 G09 G10  SYS / PHASE SHIFT
                #                    G11 G12                                  SYS / PHASE SHIFT
                # G L1W  0.00000                                              SYS / PHASE SHIFT
                "SYS / PHASE SHIFT": {
                    "parser": self._parse_phase_shift,
                    "fields": {
                        "sat_sys": (0, 1),
                        "obs_type": (2, 5),
                        "correction": (6, 14),
                        "num_satellite": (16, 18),
                        "satellites": (19, 59),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #  22 R01  1 R02 -4 R03  5 R04  6 R05  1 R06 -4 R07  5 R08  6 GLONASS SLOT / FRQ #
                #     R09 -6 R10 -7 R11  0 R13 -2 R14 -7 R15  0 R17  4 R18 -3 GLONASS SLOT / FRQ #
                #     R19  3 R20  2 R21  4 R22 -3 R23  3 R24  2               GLONASS SLOT / FRQ #
                "GLONASS SLOT / FRQ #": {
                    "parser": self._parse_glonass_slot,
                    "fields": {
                        "num_satellite": (0, 3),
                        "slot_01": (4, 11),
                        "slot_02": (11, 18),
                        "slot_03": (18, 25),
                        "slot_04": (25, 32),
                        "slot_05": (32, 39),
                        "slot_06": (39, 46),
                        "slot_07": (46, 53),
                        "slot_08": (53, 60),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #  C1C  -10.000 C1P  -10.123 C2C  -10.432 C2P  -10.634        GLONASS COD/PHS/BIS
                "GLONASS COD/PHS/BIS": {
                    "parser": self._parse_glonass_code_phase_bias,
                    "fields": {"type_01": (1, 13), "type_02": (14, 26), "type_03": (27, 39), "type_04": (40, 52)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     16    17  1851     3                                    LEAP SECONDS
                "LEAP SECONDS": {
                    "parser": self._parse_leap_seconds,
                    "fields": {
                        "leap_seconds": (0, 6),
                        "future_past_leap_seconds": (6, 12),
                        "week": (12, 18),
                        "week_day": (18, 24),
                        "time_sys": (24, 27),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #     71                                                      # OF SATELLITES
                "# OF SATELLITES": {"parser": self._parse_integer, "fields": {"num_satellites": (0, 6)}},
                # TODO: 'PRN / # OF OBS'
            },
        )

        # Parser for RINEX observation blocks

        # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8----+----9
        # > 2006 03 24 13 10 36.0000000  0  5      -0.123456789012
        # G06  23629347.915            .300 8         -.353 4  23629347.158          24.158
        # G09  20891534.648           -.120 9         -.358 6  20891545.292          38.123
        # E11          .324 8          .178 7
        # S20  38137559.506      335849.135 9
        obs_parser = ParserDef(
            end_marker=lambda _l, _ln, next_line: next_line.startswith(">"),
            label=lambda line, _ln: (
                line[0:1].isalpha()  # Obs line start with sat. system identifier
                and not line.startswith(">")  # Observation epoch line starts with '>'
                and not line[60:61].isalpha()
            ),  # Comment line
            parser_def={
                False: {
                    "parser": self._parse_observation_epoch,
                    "fields": {
                        "year": (2, 6),
                        "month": (7, 9),
                        "day": (10, 12),
                        "hour": (13, 15),
                        "minute": (16, 18),
                        "second": (18, 29),
                        "epoch_flag": (31, 32),
                        "num_sat": (32, 35),
                        "rcv_clk_offset": (41, 56),
                        "comment": (60, 80),
                    },
                },
                True: {
                    "parser": self._parse_observation,
                    "strip": "\n",  # Remove only newline '\n' leading and trailing characters from line.
                    "fields": {
                        "sat": (0, 3),
                        "obs": (3, None),  # 'None' indicates, that line is sliced until the end of line.
                    },
                },
            },
        )

        return itertools.chain([header_parser], itertools.repeat(obs_parser))

    #
    # HEADER PARSERS
    #
    def _parse_approx_position(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse station coordinates defined in RINEX header to instance variable `data`.
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

    def _parse_glonass_code_phase_bias(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse GLONASS phase correction in RINEX header to instance variable `meta['glonass_bias']`.

            self.meta['glonass_bias'] = { <obstype>: <bias in meters>}
        """
        self.meta.setdefault("glonass_bias", {})
        for field in sorted([f for f in line if f.startswith("type_")]):
            if line[field]:
                type_, bias = line[field].split()[0:2]
                self.meta["glonass_bias"].update({type_: float(bias)})

    def _parse_glonass_slot(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse GLONASS slot and frequency numbers given in RINEX header to instance variable `meta['glonass_slot']`.

            self.meta['glonass_slot'] = { <slot>: <frequency number>}
        """
        self.meta.setdefault("glonass_slot", {})
        for field in sorted([f for f in line if f.startswith("slot_")]):
            if line[field]:
                slot, freq = line[field].split()[0:2]
                self.meta["glonass_slot"].update({slot: int(freq)})

    def _parse_integer(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse integer entries of RINEX header to instance variable `meta`.
        """
        self.meta.update({k: int(v) for k, v in line.items()})

    def _parse_leap_seconds(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `LEAP SECONDS` to instance variable `meta`.

            self.meta['leap_seconds'] = { 'leap_seconds': <value>,
                                          'future_past_leap_seconds': <value>,
                                          'week': <value>,
                                          'week_day': <value>,
                                          'time_sys': <system> }
        """
        for field in line:
            self.meta.setdefault("leap_seconds", {}).update({field: line[field]})

    def _parse_phase_shift(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `SYS / PHASE SHIFT` to instance variable `meta`.

            self.meta['phase_shift'] = { <sat_sys>: { <obs_type>: { corr: <correction>,
                                                                    sat: <[satellite list]>}}}

        Example of `phase_shift` meta entry:

            self.meta['phase_shift'] =  {'G': {'L1C': {'corr': '0.00000',
                                                       'sat': ['G01', 'G02', 'G03', ...]},
                                               'L1W': {'corr': '0.00000',
                                                       'sat': []}},
                                         'R': {'L1C': {'corr': '0.00000',
                                                       'sat': ['R01', 'R02', 'R07', 'R08']}}}

        TODO: Maybe better to add information to meta['obstypes']?
        """
        self.meta.setdefault("phase_shift", {})

        if line["sat_sys"]:
            cache["sat_sys"] = line["sat_sys"]
            cache["obs_type"] = line["obs_type"]
            cache["corr"] = line["correction"]
            cache["sat"] = []

        if cache["sat_sys"] not in self.meta["phase_shift"]:
            self.meta["phase_shift"].update({cache["sat_sys"]: {}})

        cache["sat"].extend(line["satellites"].split())

        if cache["obs_type"]:
            self.meta["phase_shift"][cache["sat_sys"]].update(
                {cache["obs_type"]: {"corr": cache["corr"], "sat": cache["sat"]}}
            )

    def _parse_scale_factor(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `SYS / SCALE FACTOR` to instance variable `meta`.
        """
        log.fatal("Reading and applying of RINEX header entry 'SYS / SCALE FACTOR' is not implemented")

    def _parse_string(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse string entries of RINEX header to instance variable 'meta'.
        """
        self.meta.update({k: v for k, v in line.items()})

    def _parse_sys_dcbs_applied(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `SYS / DCBS APPLIED` to instance variable `meta`.

            self.meta['dcbs_applied'] = { <sat_sys>: { prg: <used program>,
                                                       url: <source url>}}
        """
        self.meta.setdefault("dcbs_applied", {}).update(
            {line["sat_sys"]: {"prg": line["program"], "url": line["source"]}}
        )

    def _parse_sys_obs_types(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation types given in RINEX header to instance variable `meta['obstypes']` and data.

        The data dictionaries `obs`, `cycle_slip` and `signal_strength` are initialized based on the given observation
        type in the RINEX header.

            self.meta['obstypes'] = { <sat_sys>: [<ordered list with given observation types>]}
        """
        self.data.setdefault("obs", {})
        self.data.setdefault("cycle_slip", {})
        self.data.setdefault("signal_strength", {})
        self.meta.setdefault("obstypes", {})

        if line["satellite_sys"]:
            cache["sys"] = line["satellite_sys"]
            cache["obstypes"] = list()

        for field in sorted([f for f in line if f.startswith("type_")]):
            if line[field]:
                cache["obstypes"].append(line[field])
                if line[field] not in self.obstypes_all:
                    self.obstypes_all.append(line[field])
                self.meta["obstypes"].update({cache["sys"]: cache["obstypes"]})
                self.data["obs"][line[field]] = list()
                self.data["cycle_slip"][line[field]] = list()
                self.data["signal_strength"][line[field]] = list()

    def _parse_sys_pcvs_applied(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `SYS / PCVS APPLIED` to instance variable `meta`.

            self.meta['pcvs_applied'] = { <sat_sys>: { prg: <used program>,
                                                       url: <source url>}}
        """
        self.meta.setdefault("pcvs_applied", {}).update(
            {line["sat_sys"]: {"prg": line["program"], "url": line["source"]}}
        )

    def _parse_time_of_first_obs(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse time of first observation given in RINEX header to instance variable `meta`.
        """
        if line["time_sys"] != "GPS":
            log.fatal(f"Time system {line['time_sys']} is not handled so far in Where")

        if line["time_sys"] not in self.meta:
            self.meta["time_sys"] = line["time_sys"]
        else:
            if line["time_sys"] != self.meta["time_sys"]:
                log.fatal(
                    f"Time system definition in 'TIME OF FIRST OBS' ({line['time_sys']}) "
                    f"and 'TIME OF LAST OBS' ({self.meta['time_sys']}) are not identical"
                )

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
            log.fatal(f"Time system {line['time_sys']} is not handled so far in Where.")

        if line["time_sys"]:
            if line["time_sys"] not in self.meta:
                self.meta["time_sys"] = line["time_sys"]
            else:
                if line["time_sys"] != self.meta["time_sys"]:
                    log.fatal(
                        f"Time system definition in 'TIME OF FIRST OBS' ({self.meta['time_sys']}) "
                        f"and 'TIME OF LAST OBS' ({line['time_sys']}) are not identical"
                    )

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

    #
    # OBSERVATION PARSERS
    #
    def _parse_observation_epoch(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation epoch information of RINEX observation record

        In addition the RINEX observation are decimated based on the given sampling rate.
        """
        # Reject empty line -> TODO: Better solution?
        if not line["year"].isnumeric():
            return

        # Reject comment line
        if line["comment"][0:1].isalpha():
            return

        cache["obs_time"] = "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:010.7f}" "".format(
            year=int(line["year"]),
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

        if line["epoch_flag"].strip() != "0":
            log.fatal(
                f"Epoch {cache['obs_time']} is not ok, which is indicated by epoch flag {line['epoch_flag']}.\n"
                "TODO: How should it be handled in Midgard?"
            )  # TODO: Handle flagged epochs

        # Decimate RINEX observation defined by sampling rate [seconds]
        if self.sampling_rate:
            if cache["obs_sec"] % self.sampling_rate != 0:
                cache["obs_sec"] = None  # Ignore epoch

    def _parse_observation(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation record of RINEX file

        In addition the RINEX observation are rejected from satellites not given in configuration file.
        """
        # Ignore epochs based on sampling rate
        sec = cache["obs_sec"]
        if sec is None:
            return

        # Fit length of observation line against definition (16 characters * number of observation types)
        #
        # NOTE: This is necessary, because missing observations are written as 0.0 or BLANK in RINEX format. Therefore
        #       the last observation can be BLANK. In this case the length of observation line does not fit the
        #       definition (16 characters * number of observation types), which is assumed by reading the observation
        #       line in the following.
        sys = line["sat"][0]
        num_obstypes = len(self.meta["obstypes"][sys])
        field_length = 16
        line_length = field_length * num_obstypes
        line["obs"] = line["obs"].ljust(line_length)

        # Parse observation line in fields
        for idx, obs_type in zip(range(0, line_length, field_length), self.meta["obstypes"][sys]):
            value = line["obs"][idx : idx + field_length]
            self.data["obs"][obs_type].append(_float(value[0:14]))
            self.data["cycle_slip"][obs_type].append(_float(value[14:15]))
            self.data["signal_strength"][obs_type].append(_float(value[15:16]))

        # Fill unused observation types with NaN values
        #
        # NOTE: Each observation type is saved in a Dataset field. The observation type fields have the same length
        #       to be consistent with the time, system or satellite Dataset field. The problem is that some observation
        #       types are not observed for a certain satellite system, but these observation are included with NaN
        #       values in the observation type field, which is done in the following.
        unused_obstypes = set(self.obstypes_all) - set(self.meta["obstypes"][sys])
        for obs_type in unused_obstypes:
            self.data["obs"][obs_type].append(float("nan"))
            self.data["cycle_slip"][obs_type].append(float("nan"))
            self.data["signal_strength"][obs_type].append(float("nan"))

        self.data.setdefault("time", list()).append(cache["obs_time"])
        self.data.setdefault("epoch_flag", list()).append(cache["epoch_flag"])
        self.data.setdefault("rcv_clk_offset", list()).append(cache["rcv_clk_offset"])

        obs = {
            "station": self.meta["marker_name"].lower(),  # vars['station'],
            "site_id": self.meta["marker_name"].upper(),
            "system": sys,
            "satellite": line["sat"],
            "satnum": line["sat"][1:3],
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
            # self._check_obs_data,
            self._remove_empty_systems,
            self._remove_empty_obstype_fields,
            self._time_system_correction,
            self._unit_conversion,
        ]

    def _check_obs_data(self) -> None:
        """Check availability of observation data.

        """
        # TODO: Check if data are available.

    def _remove_empty_systems(self) -> None:
        """Remove GNSSs without observations from `self.meta['obstypes']`.

        The GNSSs are defined in RINEX header (SYS / # / OBS TYPES ). It can happen, that no observations are available
        for a given GNSS. GNSSs without observations are deleted from dictionary `self.meta['obstypes']` in this
        routine.
        """
        for sys in list(self.meta["obstypes"].keys()):
            if sys not in self.data["text"]["system"]:
                log.debug(f"No observation given for GNSS {sys!r}. GNSS {sys!r} is removed from Dataset.")
                del self.meta["obstypes"][sys]

    def _remove_empty_obstype_fields(self) -> None:
        """Remove empty observation type data fields.

        The observation types given in RINEX header (SYS / # / OBS TYPES ) define the key entries initialized in the
        data dictionaries `obs`, `cycle_slip` and `signal_strength`. It can happen, that no observations are available
        for observation types defined in the RINEX header. Empty observation type entries are deleted in this routine.

        In addition it can be that the observation types are not given for a certain GNSS. In this case the observation
        types in the meta['obstypes'] variable are removed for this GNSS. But it should be kept in mind, that the
        observations for this observation type are still given in the Dataset, which are set to NaN.
        """
        remove_obstype = []  # List with observation types, which should be removed from Dataset.
        remove_obstype_sys = {}  # Dictionary with obstypes for each GNSS, should be removed from meta['obstypes'].
        for obstype, obs in self.data["obs"].items():
            if not obs or np.all(np.isnan(obs)):
                remove_obstype.append(obstype)
            systems = set(self.data["text"]["system"])
            for sys in systems:

                # Filter observations depending on GNSS
                idx = np.array(self.data["text"]["system"]) == sys

                if np.all(np.isnan(obs)[idx]):
                    remove_obstype_sys.setdefault(sys, list()).append(obstype)

        log.debug(
            f"The following observation types are removed, because no observations were found: "
            f"{' '.join(sorted(remove_obstype))}"
        )

        # Remove empty observation type data fields
        for obstype in remove_obstype:
            for sys in list(self.meta["obstypes"]):
                if obstype in self.meta["obstypes"][sys]:
                    self.meta["obstypes"][sys].remove(obstype)

            del self.data["obs"][obstype]
            del self.data["cycle_slip"][obstype]
            del self.data["signal_strength"][obstype]

        # Remove empty observation types for a given GNSS from meta['obstypes'] and other meta variables
        for sys, obstypes in remove_obstype_sys.items():
            for obstype in obstypes:
                if obstype in self.meta["obstypes"][sys]:
                    self.meta["obstypes"][sys].remove(obstype)

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

        Note, that in the RINEX format (see section 8.1 in :cite:`rinex3`) GLONASS time has the same hours as UTC and
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
    #    See section 8.2 in :cite:`rinex3`.
    #    TODO: Is it necessary to correct the pseudorange observation depending on used time system?
    #    """

    #
    # WRITE DATA
    #
    def as_dataset(self) -> "Dataset":
        """Store GNSS data in a dataset

        Returns:
            dset (Dataset): The Dataset where GNSS observation are stored with following fields:

       |  Field               | Type              | Description                                                           |
       |----------------------|-------------------|-----------------------------------------------------------------------|
       | <observation type>   | numpy.ndarray     | GNSS observation type data (e.g. C1C, C2W, L1C, L2W, ...) given       |
       |                      |                   | in meters                                                             |
       | epoch_flag           | numpy.ndarray     | Epoch flag                                                            |
       | rcv_clk_offset       | numpy.ndarray     | Receiver clock offset in seconds given for each epoch                 |
       | satellite            | numpy.ndarray     | Satellite PRN number together with GNSS identifier (e.g. G07)         |
       | satnum               | numpy.ndarray     | Satellite PRN number (e.g. 07)                                        |
       | site_pos             | PositionTable     | PositionTable object with given station coordinates (read from        |
       |                      |                   | RINEX header)                                                         |
       | station              | numpy.ndarray     | Station name list                                                     |
       | system               | numpy.ndarray     | GNSS identifier                                                       |
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
       | ant_vehicle_x       | float | X-coordinate in body-fixed coord. system of antenna reference point on vehicle     |
       | ant_vehicle_y       | float | Y-coordinate in body-fixed coord. system of antenna reference point on vehicle     |
       | ant_vehicle_z       | float | Z-coordinate in body-fixed coord. system of antenna reference point on vehicle     |
       | comment             | list  | List with RINEX header comment lines                                               |
       | dcbs_applied        | dict  | Satellite system dependent information about applying DCBs                         |
       | file_created        | str   | Date and time of file creation                                                     |
       | file_type           | str   | File type (e.g. 'O' for observation data)                                          |
       | glonass_bias        | dict  | GLONASS phase bias correction in meters given for code observation type (C1C, C1P, |
       |                     |       | C2C and/or C2P)                                                                    |
       | glonass_slot        | dict  | GLONASS frequency numbers given for GLONASS slot                                   |
       | interval            | float | Observation interval in seconds                                                    |
       | leap_seconds        | dict  | Dictionary with information related to leap seconds                                |
       | marker_name         | str   | Name of antenna marker                                                             |
       | marker_number       | str   | Number of antenna marker                                                           |
       | num_satellites      | int   | Number of satellites, for which observations are stored in the RINEX file          |
       | observer            | str   | Name of observer                                                                   |
       | obstypes            | dict  | Observation types given for each GNSS                                              |
       | pcvs_applied        | dict  | Satellite system dependent information about applying PCVs                         |
       | phase_shift         | dict  | Phase shift correction given for a satellite system dependent observation type     |
       | program             | str   | Name of program creating current file                                              |
       | rcv_clk_offset_flag | str   | Flag (1=yes, 0=no) indicating if realtime-derived receiver clock offset is         |
       |                     |       | applied for epoch, code, and phase                                                 |
       | receiver_number     | str   | Receiver serial number                                                             |
       | receiver_type       | str   | Receiver type                                                                      |
       | receiver_version    | str   | Receiver firmware version                                                          |
       | run_by              | str   | Name of agency creating current file                                               |
       | sat_sys             | str   | Satellite system given in observation file (G, R, E, J, C, I, S or M)              |
       | signal_strength_unit| str   | Unit of the carrier to noise ratio observables                                     |
       | time_first_obs      | str   | Time of first observation record                                                   |
       | time_last_obs       | str   | Time of last observation record                                                    |
       | time_sys            | str   | Time system used for GNSS observations (GPS, GLO, GAL, QZS, BDT or IRN)            |
       | version             | str   | Format version                                                                     |
        """
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
