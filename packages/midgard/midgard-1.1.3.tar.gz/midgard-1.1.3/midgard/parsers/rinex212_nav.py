"""A parser for reading GNSS RINEX navigation file (exception GLONASS and SBAS)

Example:
--------
    from midgard import parsers

    # Parse data
    parser = parsers.parse_file(parser_name="rinex212_nav", file_path=file_path)

    # Get Dataset with parsed data
    dset = parser.as_dataset()


Description:
------------

Reads GNSS data from files in the RINEX navigation file format 2.12 (see :cite:`rinex2`). An exception is, that this
parser does not handle GLONASS and SBAS navigation messages. All navigation time epochs (time of clock (toc)) are
converted to GPS time scale.

The navigation message is not defined for GALILEO, BeiDou, QZSS and IRNSS in RINEX format 2.12. In this case the RINEX
3.03 definition is used (see :cite:`rinex3`).

"""

# Standard library imports
from datetime import datetime, timedelta
import dateutil.parser
import itertools
from typing import Any, Callable, Dict, Iterable, List, Tuple, Union

# External library imports
import numpy as np

# Midgard imports
from midgard.parsers import ChainParser, ParserDef
from midgard.data import dataset
from midgard.data.time import Time
from midgard.dev import log
from midgard.dev import plugins


# TODO: SYSTEM_TIME_OFFSET_TO_GPS_SECOND & SYSTEM_TIME_OFFSET_TO_GPS_WEEK should be placed in constant.conf

# The constant shows the 'second' relation between the GNSS time systems to the GPS time scale. Galileo (E),
# IRNSS (I) and QZSS (J) uses the same second as the GPS time scale, but BeiDou (C) BDT time system is 14 seconds
# behind GPS time.
SYSTEM_TIME_OFFSET_TO_GPS_SECOND = dict(C=14, E=0, I=0, J=0)

# The constant shows the relation between the GNSS week to the GPS week. Galileo (E), IRNSS (I) and QZSS (J) week
# corresponds to GPS week, whereas BeiDou (C) week starts at GPS week 1356.
SYSTEM_TIME_OFFSET_TO_GPS_WEEK = dict(C=1356, E=0, I=0, J=0)

# The constant shows the relation between the navigation file extensions and the GNSS.
SYSTEM_FILE_EXTENSION = {"n": "G", "g": "R", "l": "E"}

# Variable name definition for specific elements in the navigation records, which are GNSS dependent.
SYSNAMES = dict(
    gnss_data_info={"G": "codes_l2", "J": "codes_l2", "E": "data_source"},
    gnss_interval={"G": "fit_interval", "J": "fit_interval", "C": "age_of_clock_corr"},
    gnss_iodc_groupdelay={"G": "iodc", "J": "iodc", "E": "bgd_e1_e5b", "C": "tgd_b2_b3"},
    gnss_l2p_flag={"G": "l2p_flag", "J": "l2p_flag"},
    gnss_tgd_bgd={"G": "tgd", "J": "tgd", "E": "bgd_e1_e5a", "C": "tgd_b1_b3", "I": "tgd"},
)


@plugins.register
class Rinex212NavParser(ChainParser):
    """A parser for reading RINEX navigation file

    The parser reads GNSS broadcast ephemeris in RINEX format 2.12 (see :cite:`rinex2`).

    #TODO: Would it not be better to use one leading underscore for non-public methods and instance variables.

    Attributes:
        data (Dict):                  The (observation) data read from file.
        data_available (Boolean):     Indicator of whether data are available.
        file_encoding (String):       Encoding of the datafile.
        file_path (Path):             Path to the datafile that will be read.
        meta (Dict):                  Metainformation read from file.
        parser_name (String):         Name of the parser (as needed to call parsers.parse_...).        
        system (String):              GNSS identifier.

    Methods:
        as_dataframe()                Return the parsed data as a Pandas DataFrame
        as_dataset()                  Return the parsed data as a Midgard Dataset
        as_dict()                     Return the parsed data as a dictionary
        parse()                       Parse data
        parse_line()                  Parse line
        postprocess_data()            Do simple manipulations on the data after they are read
        read_data()                   Read data from the data file
        setup_parser()                Set up information needed for the parser
        setup_postprocessors()        List postprocessors that should be called after parsing

        _check_nav_message()          Check correctness of navigation message
        _get_system_from_file_extension()  Get GNSS by reading RINEX navigation file extension
        _parse_file()                 Read a data file and parse the content
        _parse_ionospheric_corr()     Parse entries of RINEX header `IONOSPHERIC CORR` to instance variable `meta`.
        _parse_leap_seconds()         Parse entries of RINEX header `LEAP SECONDS` to instance variable `meta`.
        _parse_obs_float()            Parse float entries of RINEX navigation data block to instance variable 'data'.
        _parse_observation_epoch()    Parse observation epoch information of RINEX navigation data record
        _parse_string()               Parse string entries of SP3 header to instance variable 'meta'
        _parse_string_list()          Parse string entries of RINEX header to instance variable 'meta' in a list
        _parse_time_system_corr()     Parse entries of RINEX header `TIME SYSTEM CORR` to instance variable `meta`.
        _rename_fields_based_on_system()  Rename general GNSS fields to GNSS specific ones
        _time_system_correction()     Apply correction to given time system for getting GPS time scale
    """

    def __init__(self, *args: Tuple[Any], **kwargs: Dict[Any, Any]):
        """
        Args:
            args:   Parameters without keyword.
            kargs:  Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.system = self._get_system_from_file_extension()  # TODO: Check design of solution?

    def _get_system_from_file_extension(self) -> None:
        """Get GNSS by reading RINEX navigation file extension

        For RINEX 2.12 navigation files is only the file extension an indicator, which GNSS is used.

        """
        try:
            file_extension = self.file_path.suffixes[0]
        except IndexError:
            log.fatal(
                f"RINEX 2.12 navigation file extension '{file_extension}' of file {self.file_path} does not exists or "
                f"is not handled by Midgard. Following RINEX navigation file extensions should be used: "
                f"{', '.join(SYSTEM_FILE_EXTENSION.keys())}, rnx."
            )

        file_name = self.file_path.stem if ".gz" in self.file_path.suffixes else self.file_path.name
        
        return file_name[-6].upper() if ".rnx" in file_extension else SYSTEM_FILE_EXTENSION[file_extension[-1].lower()]

    #
    # PARSERS
    #
    def setup_parser(self) -> Iterable[ParserDef]:
        """Parsers defined for reading RINEX navigation file line by line

           First the RINEX header information are read and afterwards the RINEX navigation data block.
        """
        # Parser for RINEX header
        header_parser = ParserDef(
            end_marker=lambda line, _ln, _n: line[60:73] == "END OF HEADER",
            label=lambda line, _ln: line[60:].strip(),
            parser_def={
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                #      2.12           N: GPS NAV DATA                         RINEX VERSION / TYPE
                "RINEX VERSION / TYPE": {
                    "parser": self._parse_string,
                    "fields": {"version": (0, 20), "file_type": (20, 21)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # CCRINEXN V1.6.0 UX  CDDIS               01-MAR-16 19:39     PGM / RUN BY / DATE
                "PGM / RUN BY / DATE": {
                    "parser": self._parse_string,
                    "fields": {"program": (0, 20), "run_by": (20, 40), "file_created": (40, 60)},
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # IGS BROADCAST EPHEMERIS FILE                                COMMENT
                "COMMENT": {"parser": self._parse_string_list, "fields": {"comment": (0, 60)}},
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # GPSA   4.6566D-09  1.4901D-08 -5.9605D-08 -1.1921D-07       IONOSPHERIC CORR
                # GPSB   8.1920D+04  8.1920D+04 -6.5536D+04 -5.2429D+05       IONOSPHERIC CORR
                "IONOSPHERIC CORR": {
                    "parser": self._parse_ionospheric_corr,
                    "fields": {
                        "gnss_id": (0, 4),
                        "para_1": (5, 17),
                        "para_2": (17, 29),
                        "para_3": (29, 41),
                        "para_4": (41, 53),
                        "time_mark": (54, 55),
                        "sv_id": (56, 58),
                    },
                },
                # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
                # GPUT  4.6566128730D-09 1.065814103D-14 233472 2060          TIME SYSTEM CORR
                "TIME SYSTEM CORR": {
                    "parser": self._parse_time_system_corr,
                    "fields": {"corr_type": (0, 4), "a0": (5, 22), "a1": (22, 38), "t": (38, 45), "w": (45, 50)},
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
            },
        )

        # Parser for RINEX navigation data blocks

        # ----+----1----+----2----+----3----+----4----+----5----+----6----+----7----+----8
        #  1 16  3  1  0  0  0.0 0.130985863507D-04 0.102318153950D-11 0.000000000000D+00
        #     0.300000000000D+02-0.152187500000D+02 0.451304504878D-08-0.111734822451D+01
        #    -0.806525349617D-06 0.509567500558D-02 0.698119401932D-05 0.515365027618D+04
        #     0.172800000000D+06 0.119209289551D-06-0.654720735518D+00-0.540167093277D-07
        #     0.963950790865D+00 0.247875000000D+03 0.460218159465D+00-0.807676503456D-08
        #     0.664313395959D-10 0.100000000000D+01 0.188600000000D+04 0.000000000000D+00
        #     0.200000000000D+01 0.000000000000D+00 0.512227416039D-08 0.300000000000D+02
        #     0.172800000000D+06 0.000000000000D+00 0.000000000000D+00 0.000000000000D+00
        data_parser = ParserDef(
            end_marker=lambda _l, line_num, _n: line_num == 8,
            label=lambda _l, line_num: line_num,
            parser_def={
                1: {
                    "parser": self._parse_observation_epoch,
                    "fields": {
                        "sat": (0, 2),
                        "year": (2, 5),
                        "month": (5, 8),
                        "day": (8, 11),
                        "hour": (11, 14),
                        "minute": (14, 17),
                        "second": (17, 22),
                        "sat_clock_bias": (22, 41),
                        "sat_clock_drift": (41, 60),
                        "sat_clock_drift_rate": (60, 79),
                    },
                },
                2: {
                    "parser": self._parse_obs_float,
                    "fields": {"iode": (0, 22), "crs": (22, 41), "delta_n": (41, 60), "m0": (60, 79)},
                },
                3: {
                    "parser": self._parse_obs_float,
                    "fields": {"cuc": (0, 22), "e": (22, 41), "cus": (41, 60), "sqrt_a": (60, 79)},
                },
                4: {
                    "parser": self._parse_obs_float,
                    "fields": {"toe": (0, 22), "cic": (22, 41), "Omega": (41, 60), "cis": (60, 79)},
                },
                5: {
                    "parser": self._parse_obs_float,
                    "fields": {"i0": (0, 22), "crc": (22, 41), "omega": (41, 60), "Omega_dot": (60, 79)},
                },
                6: {
                    "parser": self._parse_obs_float,
                    "fields": {
                        "idot": (0, 22),
                        "gnss_data_info": (22, 41),
                        "gnss_week": (41, 60),
                        "gnss_l2p_flag": (60, 79),
                    },
                },
                7: {
                    "parser": self._parse_obs_float,
                    "fields": {
                        "sv_accuracy": (0, 22),
                        "sv_health": (22, 41),
                        "gnss_tgd_bgd": (41, 60),
                        "gnss_iodc_groupdelay": (60, 79),
                    },
                },
                8: {
                    "parser": self._parse_obs_float,
                    "fields": {
                        "transmission_time": (0, 22),
                        "gnss_interval": (22, 41),
                        # 'spare1':               (41, 60), # Blank field
                        # 'spare2':               (60, 79), # Blank field
                    },
                },
            },
        )

        return itertools.chain([header_parser], itertools.repeat(data_parser))

    def _parse_ionospheric_corr(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `IONOSPHERIC CORR` to instance variable `meta`.

                self.meta['iono_para'] = { <gnss_id>: { 'para': [<parameter list>],
                                                        'sv_id': <id>,
                                                        'time_mark': <value> }}

           The ionospheric correction parameters are GNSS dependent. In the following a list with GNSS idendifiers
           and belonging ionosphere correction parameters is shown:

            | GNSS ID    | Parameters      | Description                                                            |
            |------------|-----------------|------------------------------------------------------------------------|
            | GAL        | ai0 - ai2       | Parameters needed for NeQuick model (see Section 5.1.6 in              |
            |            |                 | :cite:`galileo-os-sis-icd`)                                            |
            | GPSA       | alpha0 - alpha3 | Parameters needed for Klobuchar model (see Section 20.3.3.5.2.5 in     |
            |            |                 | :cite:`is-gps-200h`)                                                   |
            | GPSB       | beta0 - beta3   | Parameters needed for Klobuchar model (see Section 20.3.3.5.2.5 in     |
            |            |                 | :cite:`is-gps-200h`)                                                   |
            | QZSA       | alpha0 - alpha3 | Parameters needed for Klobuchar model (see Section 5.2.4.7 in          |
            |            |                 | :cite:`bds-sis-icd-20`)                                                |
            | QZSB       | beta0 - beta3   | Parameters needed for Klobuchar model (see :cite:`is-qzss`)            |
            | BDSA       | alpha0 - alpha3 | Parameters needed for Klobuchar model (see :cite:`is-qzss`)            |
            | BDSB       | beta0 - beta3   | Parameters needed for Klobuchar model (see Section 5.2.4.7 in          |
            |            |                 | :cite:`bds-sis-icd-20`)                                                |
            | IRNA       | alpha0 - alpha3 | Parameters needed for Klobuchar model (see Appendix H in               |
            |            |                 | :cite:`irnss-icd-sps`)                                                 |
            | IRNB       | beta0 - beta3   | Parameters needed for Klobuchar model (see Appendix H in               |
            |            |                 | :cite:`irnss-icd-sps`)                                                 |

        """
        para = list()

        # Save ionospheric correction parameters in a list
        for field in sorted([f for f in line if f.startswith("para_")]):
            para.append(_float(line[field]))

        self.meta.setdefault("iono_para", dict()).update(
            {line["gnss_id"]: {"para": para, "sv_id": line["sv_id"], "time_mark": line["time_mark"]}}
        )

    def _parse_leap_seconds(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `LEAP SECONDS` to instance variable `meta`.

            self.meta['leap_seconds'] = { 'leap_seconds': <value>,
                                          'future_past_leap_seconds': <value>,
                                          'week': <value>,
                                          'week_day': <value>,
                                          'time_sys': <system> }
        """
        for field in line:
            self.meta.setdefault("leap_seconds", dict()).update({field: line[field]})

    def _parse_obs_float(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse float entries of RINEX navigation data block to instance variable 'data'.
        """

        # TODO: RINEX header in between the navigation message blocks is not handled so far!!! Following lines are only
        #      a workaround to skip these RINEX header lines.
        if "skip_additional_header_line" in cache:
            return

        for k, v in line.items():
            self.data.setdefault(k, list()).append(_float(v))

    def _parse_string(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse string entries of RINEX header to instance variable 'meta'
        """
        for k, v in line.items():
            self.meta[k] = v

    def _parse_string_list(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse string entries of RINEX header to instance variable 'meta' in a list
        """
        for k, v in line.items():
            self.meta.setdefault(k, list()).append(v)

    def _parse_observation_epoch(self, line: Dict[str, str], cache: Dict[str, Any]) -> None:
        """Parse observation epoch information of RINEX navigation data record

        Only the last 2-digits of the year is given in the observation epoch, therefore it is necessary to get the
        complete 4-digit year. The year can only be determined corrrectly in the time period 1980 until 2079.
        """

        # TODO: RINEX header in between the navigation message blocks is not handled so far!!! Following lines are only
        #      a workaround to skip these RINEX header lines.
        if line["sat_clock_drift_rate"][0].isalpha():
            cache["skip_additional_header_line"] = True
            return

        # Get correct 4-digit year (in observation epoch only 2-digit year is given)
        if (int(line["year"]) >= 80) and (int(line["year"]) <= 99):
            year = int("19" + line["year"].zfill(2))
        else:
            year = int("20" + line["year"].zfill(2))

        # Create Time object
        time = "{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:{second:010.7f}" "".format(
            year=year,
            month=int(line["month"]),
            day=int(line["day"]),
            hour=int(line["hour"]),
            minute=int(line["minute"]),
            second=float(line["second"]),
        )

        # Fill temporary Dataset
        self.data.setdefault("time", list()).append(time)
        sat = self.system + line["sat"].zfill(2)
        self.data.setdefault("system", list()).append(sat[0])
        self.data.setdefault("satellite", list()).append(sat)
        self.data.setdefault("sat_clock_bias", list()).append(_float(line["sat_clock_bias"]))
        self.data.setdefault("sat_clock_drift", list()).append(_float(line["sat_clock_drift"]))
        self.data.setdefault("sat_clock_drift_rate", list()).append(_float(line["sat_clock_drift_rate"]))


    def _parse_time_system_corr(self, line: Dict[str, str], _: Dict[str, Any]) -> None:
        """Parse entries of RINEX header `TIME SYSTEM CORR` to instance variable `meta`.

                self.meta['time_sys_corr'] = { <corr_type>: { 'a0': <value>,
                                                              'a1': <value>,
                                                              't':  <value>,
                                                              'w':  <value> }}

           The time system correction parameters are dependent on the given correction type, which is shown below:

            | Type       | Parameters           | Description     |
            |------------|----------------------|-----------------|
            | BDUT       | a0=A_0UTC, a1=A_1UTC | BDS to UTC      |
            | GAUT       | a0, a1               | GAL to UTC      |
            | GLGP       | a0=-TauC, a1=0       | GLO to GPS      |
            | GLUT       | a0=-TauC, a1=0       | GLO to UTC      |
            | GPGA       | a0=A0G, a1=A1G       | GPS to GAL      |
            | GPUT       | a0, a1               | GPS to UTC      |
            | IRGP       | a0=A_0UTC, a1=A_1UTC | IRN to GPS      |
            | IRUT       | a0=A_0UTC, a1=A_1UTC | IRN to UTC      |
            | QZGP       | a0, a1               | QZS to GPS      |
            | QZUT       | a0, a1               | QZS to UTC      |
            | SBUT       | a0, a1               | SBAS to UTC     |

        """
        self.meta.setdefault("time_sys_corr", dict()).update(
            {
                line["corr_type"]: {
                    "a0": _float(line["a0"]),
                    "a1": _float(line["a1"]),
                    "t": int(line["t"]),
                    "w": int(line["w"]),
                }
            }
        )

    #
    # SETUP POSTPROCESSORS
    #
    def setup_postprocessors(self) -> List[Callable[[], None]]:
        """List steps necessary for postprocessing
        """
        return [
            self._check_nav_message,
            self._rename_fields_based_on_system,
            self._time_system_correction,
            self._determine_message_type,
        ]

    def _rename_fields_based_on_system(self) -> None:
        """Rename general GNSS fields to GNSS specific ones

        Several fields in the RINEX navigation message have a different meaning depending on the GNSS. As a first step
        the RINEX navigation parser reads these fields in a general field variable like 'gnss_data_info',
        'gnss_interval', 'gnss_iodc_groupdelay', 'gnss_l2p_flag' and 'gnss_tgd_bgd'. As a second step the general
        fields are renamed in this routine depending on the GNSS. In the following table the relationship between
        the general field and the new GNSS dependent fields are shown:

       |  General field       | New field           | Description                                                       |
       |----------------------|-------------------- |-------------------------------------------------------------------|
       | gnss_data_info       |                     | Depending on GNSS this field has different meaning:               |
       |                      | E: data_source      |  - Galileo: Data source information about the broadcast           |
       |                      |                     |    ephemeris block, that means if the ephemeris block is based    |
       |                      |                     |    on FNAV or INAV navigation message.                            |
       |                      | G: codes_l2         |  - GPS: Codes on L2 channel. Indication which codes are used      |
       |                      |                     |    on L2 channel (P code, C/A code). See section 20.3.3.3.1.2     |
       |                      |                     |    in :cite:`is-gps-200h`).                                       |
       |                      | J: codes_l2         |  - QZSS: Codes on L2 channel. Indication if either C/A- or P-     |
       |                      |                     |    code is used on L2 channel (0: spare, 1: P-code, 2: L1C/A      |
       |                      |                     |    code). See section 4.1.2.7 in :cite:`is-qzss-pnt-001`.         |
       |                      | C, I, R: None       |  - BeiDou, IRNSS and GLONASS: not used                            |
       |                      |                     |                                                                   |
       | gnss_interval        |                     | Interval indicates either the curve-fit interval for GPS or QZSS  |
       |                      |                     | ephemeris or for BeiDou the extrapolation interval for clock      |
       |                      |                     | correction parameters:                                            |
       |                      |                     | BeiDou to the clock correction parameters:                        |
       |                      | C: age_of_clock_corr|   - BeiDou: Age of data, clock (AODC) is the extrapolated         |
       |                      |                     |     interval of clock correction parameters. It indicates the time|
       |                      |                     |     difference between the reference epoch of clock correction    |
       |                      |                     |     parameters and the last observation epoch for extrapolating   |
       |                      |                     |     clock correction parameters. Meaning of AODC                  |
       |                      |                     |      < 25  Age of the satellite clock correction parameters in    |
       |                      |                     |            hours                                                  |
       |                      |                     |        25  Age of the satellite clock correction parameters is    |
       |                      |                     |            two days                                               |
       |                      |                     |        ...                                                        |
       |                      |                     |     See section 5.2.4.9 in :cite:`bds-sis-icd`.                   |
       |                      | G: fit_interval     |   - GPS: Indicates the curve-fit interval used by the GPS Control |
       |                      |                     |     Segment in determining the ephemeris parameters, which is     |
       |                      |                     |     given in HOURS (see section 6.6 in :cite:`rinex2`).           |
       |                      | J: fit_interval     |   - QZSS: Fit interval is given as flag (see section 4.1.2.7 in   |
       |                      |                     |     :cite:`is-qzss-pnt-001`)                                      |
       |                      |                     |           0 - 2 hours                                             |
       |                      |                     |           1 - more than 2 hours                                   |
       |                      |                     |           blank - not known                                       |
       |                      | E, I, R: None       |   - Galileo, IRNSS and GLONASS: not used                          |
       |                      |                     |                                                                   |
       | gnss_iodc_groupdelay |                     | Clock issue of data or group delay depending on GNSS:             |
       |                      | C: tgd_b2_b3        |   - BeiDou: B2/B3 TGD2                                            |
       |                      | E: bgd_e1_e5b       |   - Galileo: E1-E5b BGD (see section 5.1.5 in                     |
       |                      |                     |     :cite:`galileo-os-sis-icd`)                                   |
       |                      | G: iodc             |   - GPS: IODC (Clock issue of data indicates changes              |
       |                      |                     |     (set equal to IODE))                                          |
       |                      | J: iodc             |   - QZSS: IODC                                                    |
       |                      | I, R: None          |   - IRNSS and GLONASS: not used                                   |
       |                      |                     |                                                                   |
       | gnss_l2p_flag        |                     | L2 P-code data flag is only used by GPS and QZSS:                 |
       |                      | G: l2p_flag         |   - GPS: When bit 1 of word four is a "1", it shall indicate that |
       |                      |                     |     the NAV data stream was commanded OFF on the P-code of the L2 |
       |                      |                     |     channel (see section 20.3.3.3.1.6 in :cite:`is-gps-200h`).    |
       |                      | J: l2p_flag         |   - QZSS: L2P data flag set to 1 since QZSS does not track L2P.   |
       |                      |                     |     See section 4.1.2.7 in :cite:`is-qzss-pnt-001`.               |
       |                      | C, E, I, R: None    |   - BeiDou, Galileo, IRNSS and GLONASS: not used                  |
       |                      |                     |                                                                   |
       | gnss_tgd_bgd         |                     | Total group delay (TGD) or broadcast group delay (BGD) for        |
       |                      |                     | Galileo:                                                          |
       |                      | C: tgd_b1_b3        |   - BeiDou: B1/B3 TGD1                                            |
       |                      | E: bgd_e1_e5a       |   - Galileo: E1-E5a BGD (see section 5.1.5 in                     |
       |                      |                     |     :cite:`galileo-os-sis-icd`)                                   |
       |                      | G: tgd              |   - GPS: TGD (:math:`L_1 - L_2` delay correction term. See        |
       |                      |                     |     section 20.3.3.3.3.2 in :cite:`is-gps-200h`.)                 |
       |                      | I: tgd              |   - IRNSS: TGD                                                    |
       |                      | J: tgd              |   - QZSS: TGD                                                     |
       |                      | R: None             |   - GLONASS: not used                                             |
        """
        for field, names in SYSNAMES.items():
            if field in self.data:
                try:
                    new_field = names[self.system]
                except KeyError:
                    # Remove blank RINEX navigation fields, which does not support this field
                    del self.data[field]
                    continue

                if field != new_field:
                    self.data[new_field] = self.data[field]
                    del self.data[field]

    def _check_nav_message(self) -> None:
        """Check correctness of navigation message.

        Issue of ephemeris data (IODE) and clock issue of data (IODC) should be equal (see Sections 20.3.3.3.1.5,
        20.3.3.4.1 and 20.3.4.4 in :cite:`is-gps-200h`). If this is not the case, a data set cutover has occurred and
        new data must be collected.
        """
        if not self.data:
            log.fatal(f"No navigation records are given in file {self.file_path}.")
        # TODO: Check has to be done GNSS dependent!!!
        # TODO: What should be done, if this happens? Use of another navigation message?
        # if set(self.data["gnss_iodc_groupdelay"]).difference(set(self.data["iode"])):
        #    log.fatal("Issue of ephemeris data (IODE) and clock issue of data (IODC) are not equal.")

    def _determine_message_type(self) -> None:
        """Determine navigation message type and save it in 'data' dictionary under 'nav_type' key

        The navigation message type is dependent on the GNSS:
            GPS:      GPS provides LNAV and the newer CNAV and MNAV messages. LNAV and CNAV messages are civil
                      navigation messages, whereas MNAV is a military message.
            Galileo:  Galileo provides the Freely accessible (F/NAV), the Integriy (I/NAV), Commercial (C/NAV) and
                      Governmental (G/NAV) Navigation Message.

        Midgard can handle at the moment LNAV, F/NAV and I/NAV navigation messages. For further information see also
        in Section 8.3 in :cite:`rinex3` and section 5.1.3 in :cite:`galileo-os-sis-icd` (for Galileo F/NAV and I/NAV
        message).

        The mask for checking I/NAV and F/NAV navigation messages is based on RINEX 'BROADCAST ORBIT - 5' definition:
            - if bit 0 is set (e.g. 513):       E1-B signal is used for generation of I/NAV message
            - if bit 1 is set (e.g. 258):       E5a-I signal is used for generation of F/NAV message
            - if bit 2 is set (e.g. 516):       E5b-I signal is used for generation of I/NAV message
            - if bit 0 and 2 is set (e.g. 517): I/NAV message is merged together based on E1-B and E5b-I signal
            - if bit 8 is set (e.g. 258):       Satellite clock correction is given for E5a-E1 (I/NAV message) 
            - if bit 9 is set (e.g. 513):       Satellite clock correction is given for E5b-E1 (F/NAV message).
        """
        # Mask definition for Galileo navigation messages
        nav_mask = {
            # 9876543210 bit number
            0b0100000001: "INAV_E1",  # = 257     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100001001: "INAV_E1",  # = 265     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100010001: "INAV_E1",  # = 273     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100011001: "INAV_E1",  # = 281     Note: af0-af2, Toc, SISA are for E5a,E1
            0b1000000001: "INAV_E1",  # = 513  <- normally used
            0b1000001001: "INAV_E1",  # = 521
            0b1000010001: "INAV_E1",  # = 529
            0b1000011001: "INAV_E1",  # = 537
            0b1000000100: "INAV_E5b",  # = 516  <- normally used
            0b1000001100: "INAV_E5b",  # = 524
            0b1000010100: "INAV_E5b",  # = 532
            0b1000011100: "INAV_E5b",  # = 540
            0b0100000101: "INAV_E1E5b",  # = 261     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100001101: "INAV_E1E5b",  # = 269     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100010101: "INAV_E1E5b",  # = 277     Note: af0-af2, Toc, SISA are for E5a,E1
            0b0100011101: "INAV_E1E5b",  # = 285     Note: af0-af2, Toc, SISA are for E5a,E1
            0b1000000101: "INAV_E1E5b",  # = 517  <- normally used
            0b1000001101: "INAV_E1E5b",  # = 525
            0b1000010101: "INAV_E1E5b",  # = 533
            0b1000011101: "INAV_E1E5b",  # = 541
            0b0100000010: "FNAV_E5a",  # = 258  <- normally used
            0b0100001010: "FNAV_E5a",  # = 266
            0b0100010010: "FNAV_E5a",  # = 274
            0b0100011010: "FNAV_E5a",  # = 282
            0b1000000010: "FNAV_E5a",  # = 514     Note: af0-af2, Toc, SISA are for E5b,E1
            0b1000001010: "FNAV_E5a",  # = 522     Note: af0-af2, Toc, SISA are for E5b,E1
            0b1000010010: "FNAV_E5a",  # = 530     Note: af0-af2, Toc, SISA are for E5b,E1
            0b1000011010: "FNAV_E5a",  # = 538     Note: af0-af2, Toc, SISA are for E5b,E1
        }

        self.data["nav_type"] = np.full(len(self.data["time"]), "", dtype=object)

        for sys in set(self.data["system"]):
            idx = np.array(self.data["system"]) == sys

            if sys == "G":
                # NOTE: In Steigenberger et al. (2015): 'Performance Evaluation of the Early CNAV Navigation Message' do
                #      they use for CNAV navigation messages the RINEX 'IODE' record for the change rate of the semi-
                #      major axis 'aDot'. 'IODE' is an integer and 'aDot' a float value.
                if not np.all(_isinteger(np.array(self.data["iode"])[idx])):
                    log.fatal(
                        "GPS navigation message does not seem to be a LNAV message. Note: Midgard do not handle "
                        "CNAV message so far."
                    )
                self.data["nav_type"][idx] = "LNAV"

            elif sys == "E":
                # NOTE: The RINEX data source record provides information about the Galileo navigation message.
                data_source = np.array(self.data["data_source"])[idx]
                data_source[data_source == None] = 0  # Bitwise operations does not handle NoneType values
                type_tmp = np.full(len(data_source), None)

                # Loop over different Galileo navigation masks for navigation message detection
                for mask, nav_type in nav_mask.items():
                    # mask_idx = np.bitwise_and(data_source.astype(int), mask).astype(bool)
                    mask_idx = data_source.astype(int) == mask
                    type_tmp[mask_idx] = nav_type

                self.data["nav_type"][idx] = type_tmp

    def _time_system_correction(self) -> None:
        """Apply correction to given time system for getting GPS time scale

        Following relationship are given between GNSS time scale (either BeiDou, Galileo, IRNSS or QZSS)
        :math:`t_{GNSS}` and GPS time scale :math:`t_{GPS}` (see Section 2.1.4 in :cite:`teunissen2017`):
        .. math::
              t_{GPS}  = t_{GNSS} + \Delta t

        The time offset :math:`\Delta t` is 0 s for Galileo, IRNSS and QZSS and for BeiDou 14 s. All these time scales
        are related to the International Atomic Time (TAI) by a certain time offset. In addition the GNSS week number
        is different depending on the GNSS. Galileo, IRNSS and QZSS are referring to the same GPS week, whereas BeiDou
        week starts at GPS week 1356.

        In this routine the given navigation epoch (time of clock (toc)), time of ephemeris (toe) and the broadcast
        ephemeris transmission time will be transformed to GPS time scale for BeiDou, Galileo, IRNSS and QZSS.

        It can happen that the transmission time is referring to another GPS week as the navigation epoch (time of clock
        (toc)). The transmission time will be adjusted to the same GPS week of the navigation epoch.

        TODO: Is it necessary to adjust also toe, if given in RINEX format?
        TODO: Should this function be an editor instead?
        """
        system = self.system
        valid_systems = ["C", "E", "G", "I", "J"]  # R-GLONASS and S-SBAS is not handled so far in Midgard

        if system not in valid_systems:
            log.fatal(
                "Time system '{}' in file {} is not handled in Midgard. Time systems for following GNSS identifiers"
                " are defined: {}.",
                system,
                self.file_path,
                (", ").join(valid_systems),
            )

        # Time conversion is only necessary for C-BeiDou navigation files (Note: M-Mixed are not defined for RINEX 2.12
        # format)
        if system == "C":

            # Convert observation time entries to GPS time scale by adding system time offset
            self.data["time"] = [
                dateutil.parser.parse(t) + timedelta(seconds=SYSTEM_TIME_OFFSET_TO_GPS_SECOND.get(system, 0))
                for t in self.data["time"]
            ]

            self.data["toe"] = [
                t + timedelta(seconds=SYSTEM_TIME_OFFSET_TO_GPS_SECOND.get(system, 0)) for t in self.data["toe"]
            ]

            self.data["transmission_time"] = [
                t + timedelta(seconds=SYSTEM_TIME_OFFSET_TO_GPS_SECOND.get(system, 0))
                for t in self.data["transmission_time"]
            ]

            self.data["gnss_week"] = [
                w + SYSTEM_TIME_OFFSET_TO_GPS_WEEK.get(system, 0) for w in self.data["gnss_week"]
            ]

            # Convert time data entries to Time object
            self.data["time"] = Time(val=self.data["time"], scale="gps", fmt="datetime")

        else:
            # Conversion to datetime format
            # TODO workaround: "isot" does not work for initialization of time field (only 5 decimals for seconds are
            #                  allowed). Therefore self.data["time"] is converted to datetime object.
            date = []
            millisec = []
            for v in self.data["time"]:
                val, val2 = v.split(".")
                date.append(datetime.strptime(val, "%Y-%m-%dT%H:%M:%S"))
                millisec.append(timedelta(milliseconds=int(val2)))

            # Convert time data entries to Time object
            self.data["time"] = Time(val=date, val2=millisec, scale="gps", fmt="datetime")
            # TODO: Better solution: self.data["time"] = Time(self.data["time"], scale="gps", fmt="isot")

        self.data["toe"] = Time(
                            val=self.data["gnss_week"], 
                            val2=self.data["toe"], 
                            scale="gps", 
                            fmt="gps_ws",
        ) 
        self.data["transmission_time"] = Time(
                                            val=self.data["gnss_week"], 
                                            val2=self.data["transmission_time"], 
                                            scale="gps", 
                                            fmt="gps_ws",
        )

        # Handling of week crossovers - refer time of ephemeris (toe) and transmission time to same GPS week as
        # navigation epoch (time of clock (toc))
        # TODO: It is only a workaround. This should be done before generating a TimeObject!!!! Use 28.02.2016 as check.
        # TODO: Is it necessary for toe? Or is toe always refered to current GPS week?
        for field in ["toe", "transmission_time"]:
            # gpssec = self.data[field].gpssec.copy()
            gpssec = self.data[field].gps_ws.seconds
            # time_diff = self.data["time"].gpssec - gpssec
            time_diff = self.data["time"].gps_ws.seconds - gpssec
            if np.any(time_diff > 302_400):
                idx = time_diff > 302_400
                gpssec[idx] += 604_800
            elif np.any(time_diff < -302_400):
                idx = time_diff < -302_400
                gpssec[idx] -= 604_800
            self.data[field] = Time(val=self.data["gnss_week"], val2=gpssec, scale="gps", fmt="gps_ws")

    #
    # WRITE DATA
    #
    def as_dataset(self) -> "Dataset":
        """Store GNSS RINEX navigation data in a dataset

        Returns:
            Midgard Dataset where broadcast ephemeris are stored with following fields:

            
       | Field               | System | Unit            | Description                                                    |
       |---------------------|--------|-----------------|----------------------------------------------------------------|
       | age_of_clock_corr   | C      |                 | BeiDou: Age of data, clock (AODC) is the extrapolated interval |
       |                     |        |                 |   of clock correction parameters. It indicates the time        |
       |                     |        |                 |   difference between the reference epoch of clock correction   |
       |                     |        |                 |   parameters and the last observation epoch for extrapolating  |
       |                     |        |                 |   clock correction parameters. Meaning of AODC                 |
       |                     |        |                 |   < 25  Age of the satellite clock correction parameters in    |
       |                     |        |                 |         hours                                                  |
       |                     |        |                 |     25  Age of the satellite clock correction parameters is    |
       |                     |        |                 |         two days                                               |
       |                     |        |                 |    ...                                                         |
       |                     |        |                 |   See section 5.2.4.9 in :cite:`bds-sis-icd`.                  |
       | bgd_e1_e5b          |  E     |                 | Galileo: group delay E1-E5b BGD (see section 5.1.5 in          |
       |                     |        |                 |   :cite:`galileo-os-sis-icd`)                                  |
       | cic, cis            | CEGIJ  | rad             | Correction coefficients of inclination                         |
       | crc, crs            | CEGIJ  | m               | Correction coefficients of orbit radius                        |
       | cuc, cus            | CEGIJ  | rad             | Correction coefficients of argument of perigee                 |
       | codes_l2            |   G J  |                 | GPS: Codes on L2 channel. Indication which codes are used      |
       |                     |        |                 |   on L2 channel (P code, C/A code). See section 20.3.3.3.1.2   |
       |                     |        |                 |   in :cite:`is-gps-200h`).                                     |
       |                     |        |                 | QZSS: Codes on L2 channel. Indication if either C/A- or P-     |
       |                     |        |                 |   code is used on L2 channel (0: spare, 1: P-code, 2: L1C/A    |
       |                     |        |                 |   code). See section 4.1.2.7 in :cite:`is-qzss-pnt-001`.       |
       | data_source         |  E     |                 | Galileo: Data source information about the broadcast           |
       |                     |        |                 |   ephemeris block, that means if the ephemeris block is based  |
       |                     |        |                 |   on FNAV or INAV navigation message.                          |
       | delta_n             | CEGIJ  | rad/s           | Mean motion difference from computed value                     |
       | e                   | CEGIJ  |                 | Eccentricity of the orbit                                      |
       | fit_interval        |   G J  |                 | GPS: Indicates the curve-fit interval used by the GPS Control  |
       |                     |        |                 |  Segment in determining the ephemeris parameters, which is     |
       |                     |        |                 |  given in HOURS (see section 6.6 in :cite:`rinex2`).           |
       |                     |        |                 | QZSS: Fit interval is given as flag (see section 4.1.2.7 in    |
       |                     |        |                 | :cite:`is-qzss-pnt-001`):                                      |
       |                     |        |                 |    0 - 2 hours                                                 |
       |                     |        |                 |    1 - more than 2 hours                                       |
       |                     |        |                 |    blank - not known                                           |
       | gnss_week           | CEGIJ  |                 | Week number of ephemeris reference epoch, whichs depends on the|
       |                     |        |                 | used GNSS. The week number is converted to GPS week.           |
       | i0                  | CEGIJ  | rad             | Inclination angle at the reference time                        |
       | idot                | CEGIJ  | rad/s           | Rate of change of inclination angle                            |
       | iodc                |   G J  |                 | GPS: IODC (Clock issue of data indicates changes (set equal to |
       |                     |        |                 |   IODE))                                                       |
       |                     |        |                 | QZSS: IODC                                                     |
       | iode                | CEGIJ  |                 | Ephemeris issue of data indicates changes to the broadcast     |
       |                     |        |                 | ephemeris:                                                     |
       |                     |        |                 |   - GPS: Ephemeris issue of data (IODE), which is set equal to |
       |                     |        |                 |     IODC                                                       |
       |                     |        |                 |   - Galileo: Issue of Data of the NAV batch (IODnav)           |
       |                     |        |                 |   - QZSS: Ephemeris issue of data (IODE)                       |
       |                     |        |                 |   - BeiDou: Age of Data Ephemeris (AODE)                       |
       |                     |        |                 |   - IRNSS: Issue of Data, Ephemeris and Clock (IODEC)          |
       | lp2_flag            |   G J  |                 | L2 P-code data flag:                                           |
       |                     |        |                 |   - GPS: When bit 1 of word four is a "1", it shall indicate   |
       |                     |        |                 |     that the NAV data stream was commanded OFF on the P-code   |
       |                     |        |                 |     of the L2 channel (see section 20.3.3.3.1.6 in             |
       |                     |        |                 |     :cite:`is-gps-200h`).                                      |
       |                     |        |                 |   - QZSS: L2P data flag set to 1 since QZSS does not track L2P.|
       |                     |        |                 |     See section 4.1.2.7 in :cite:`is-qzss-pnt-001`.            |
       | m0                  | CEGIJ  | rad             | Mean anomaly at reference epoch                                |
       | omega               | CEGIJ  | rad             | Argument of perigee                                            |
       | Omega               | CEGIJ  | rad             | Longitude of ascending node of orbit plane at weekly epoch     |
       | Omega_dot           | CEGIJ  | rad/s           | Rate of change of right ascension of the ascending node        |
       | sat_clock_bias      | CEGIJ  | s               | Satellite clock offset from GPS time                           |
       | sat_clock_drift     | CEGIJ  | s/s             | Satellite clock frequency offset                               |
       | sat_clock_drift_rate| CEGIJ  | :math:`s/s^2`   | Satellite clock frequency drift                                |
       | satellite           | CEGIJ  |                 | Satellite PRN number                                           |
       | sqrt_a              | CEGIJ  | :math:`\sqrt{m}`| Square root of semi-major axis of the orbit                    |
       | sv_accuracy         | CEGIJ  | m               | Satellite accuracy index, which is different for GNSS:         |
       |                     |        |                 |   - GPS: SV accuracy in meters (see section 20.3.3.3.1.3 in    |
       |                     |        |                 |     :cite:`is-gps-200h`)                                       |
       |                     |        |                 |   - Galileo: SISA signal in space accuracy in meters           |
       |                     |        |                 |     (see section 5.1.11 in :cite:`galileo-os-sis-icd`)         |
       |                     |        |                 |   - BeiDou: Is that the user range accuracy index (URAI) in    |
       |                     |        |                 |     meters (see section 5.2.4.5 in :cite:`bds-sis-icd`)        |
       |                     |        |                 |   - QZSS: Is that the user range accuracy index?               |
       |                     |        |                 |     (see table 4.1.2-4 in :cite:`is-qzss-pnt-001`)             |
       |                     |        |                 |   - IRNSS: User range accuracy in meters (see section 6.2.1.4  |
       |                     |        |                 |     :cite:`irnss-icd-sps`)                                     |
       | sv_health           | CEGIJ  |                 | The definition of the satellite vehicle health flags depends on|
       |                     |        |                 | GNSS:                                                          |
       |                     |        |                 |   - GPS: see section 20.3.3.3.1.4 in :cite:`is-gps-200h`       |
       |                     |        |                 |   - Galileo: see section 5.1.9.3 in :cite:`galileo-os-sis-icd` |
       |                     |        |                 |   - BeiDou: see section 5.2.4.6 in :cite:`bds-sis-icd`         |
       |                     |        |                 |   - QZSS: see section 4.1.2.3 in :cite:`is-qzss-pnt-001`       |
       |                     |        |                 |   - IRNSS: see section 6.2.1.6 in :cite:`irnss-icd-sps`        |
       | system              | CEGIJ  |                 | GNSS identifier                                                |
       | tgd                 |   GIJ  |                 | Total group delay (TGD) for GPS, IRNSS and QZSS:               |
       |                     |        |                 |   - GPS: TGD (:math:`L_1 - L_2` delay correction term. See     |
       |                     |        |                 |     section 20.3.3.3.3.2 in :cite:`is-gps-200h`.)              |
       | tgd_b1_b3           | C      |                 | BeiDou: total group delay (TGD1) for frequencies B1/B3         |
       | tgd_b2_b3           | C      |                 | BeiDou: total group delay (TGD2) for frequencies B2/B3         |
       | time                |        |                 | Time of clock (Toc), which is related to GPS time scale. That  |
       |                     |        |                 | means all the different GNSS time systems (GPS: GPS time,      |
       |                     |        |                 | Galileo: GAL time, QZSS: QZS time, BeiDou: BDT time, IRNSS:    |
       |                     |        |                 | IRN time) are converted to GPS time scale.                     |
       | time.data           |        |                 | TODO                                                           |
       | time.utc            |        |                 | TODO                                                           |
       | toe                 | CEGIJ  | s               | Time of ephemeris, that means fractional part of current GPS   |
       |                     |        |                 | week of ephemeris reference epoch. The week is dependent       |
       |                     |        |                 | on GNSS (GPS: GPS week, Galileo: GAL week, QZSS: GPS week,     |
       |                     |        |                 | BeiDou: BDT week, IRNSS: IRN week), therefore the different    |
       |                     |        |                 | GNSS weeks are converted to GPS week.                          |
       | transmission_time   | CEGIJ  | s               | Transmission time of message converted to GPS time scale.      |

            and following Dataset `meta` data, whereby the `meta` data are saved in a dictionary with current days
            as keys:

      |  Entry              | Type  | Description                                                                |
      |---------------------|-------|----------------------------------------------------------------------------|
      | comment             | list  | List with comment lines                                                    |
      | file_created        | str   | Date of file creation                                                      |
      | file_type           | str   | File type                                                                  |
      | iono_para           | dict  | Dictionary with GNSS dependent ionospheric correction parameters (assumed  |
      |                     |       | that is defined only for GPS by using RINEX 2.12 format)                   |
      | leap_seconds        | dict  | Dictionary with information related to leap seconds (compatible with RINEX |
      |                     |       | 3.xx navigation file data struture)                                        |
      | program             | str   | Name of program creating current file                                      |
      | run_by              | str   | Name of agency creating current file                                       |
      | time_sys_corr       | dict  | Dictionary with GNSS time system corrections                               |
      | version             | str   | Format version                                                             |
        """

        dset = dataset.Dataset(num_obs=len(self.data["time"]))
        dset.meta.update(self.meta)

        for k, v in self.data.items():
            if k in ["time", "toe", "transmission_time"]:
                # MURKS, TODO: How it works to initialize time field with a Time object?
                dset.add_time(k, val=v.datetime, scale=v.scale, fmt="datetime")
            elif k in ["nav_type", "satellite", "system"]:
                dset.add_text(k, val=v)
            else:
                if isinstance(v, list):
                    dset.add_float(k, val=np.array(v))

        return dset


# TODO: Maybe better to have this routine in a module.
def _float(value: str) -> float:
    """Convert string to float value

    Convert a string to a floating point number (including, e.g. -0.5960D-01). Whitespace or empty value is set to 0.0.

    Args:
        value:   string value

    Returns:
        Float value
    """
    if value.isspace() or not value:
        return 0.0
    else:
        return float(value.replace("D", "e"))


# TODO: Maybe better to have this routine in a module.
def _isinteger(x: Union[float, np.ndarray]) -> np.ndarray:
    """Check for integer type in given array

    Args:
        x:  Float numbers

    Returns:
        Array boolean values, whereby True means integer value
    """
    return np.equal(np.mod(x, 1), 0)
