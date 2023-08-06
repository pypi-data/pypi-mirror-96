#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
#

"""  xml templates """


#: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str` , :obj:`str` > >)
#:     standard component template variables
#:     and its [default value, doc string]
standardComponentVariables = {
    'empty': {},
    'maia': {
        'runnumber': {
            'default': None,
            'doc': "run number of maia (datasource)"
        },
        'pressure': {
            'default': None,
            'doc': "gas pressure in mbar (datasource)"
        },
        'chillersetpoint': {
            'default': None,
            'doc': "chiller set point temperature in Celsus (datasource)"
        },
        'voltagesetpoint': {
            'default': None,
            'doc': "voltage set point temperature in Celsus (datasource)"
        },
        'leakagecurrent': {
            'default': None,
            'doc': "leakage current sensor for maia in A (datasource)"
        },
        'peltiercurrent': {
            'default': None,
            'doc': "peltier current sensor for maia in A (datasource)"
        },
        'watertemperature': {
            'default': None,
            'doc': "water temperature sensor for maia in Celsus (datasource)"
        },
        'chiptemperature': {
            'default': None,
            'doc': "detector chip temperature sensor for maia in Celsus "
            "(datasource)"
        },
        'mosfettemperature': {
            'default': None,
            'doc': "mosfet temperature sensor for maia in Celsus (datasource)"
        },
        'identity': {
            'default': None,
            'doc': "sensor identity for maia (datasource)"
        },
        'status': {
            'default': None,
            'doc': "interlock status for maia (datasource)"
        },
        'uptime': {
            'default': None,
            'doc': "interlock uptime for maia (datasource)"
        },
        'interlockpressure': {
            'default': None,
            'doc': "interlock pressure for maia in mbar (datasource)"
        },
        'maiastage': {
            'default': 'empty',
            'doc': "maia stage component name (component)"
        },
        'maiadimensions': {
            'default': 'empty',
            'doc': "maia dimensions component name (component)"
        },
        'maiafluxes': {
            'default': 'empty',
            'doc': "maia fluxes component name (component)"
        },
        'gaintrimenable': {
            'default': None,
            'doc': "gaintrim enable status for maia (datasource)"
        },
        'lineariseenable': {
            'default': None,
            'doc': "linearise enable status for maia (datasource)"
        },
        'photonenable': {
            'default': None,
            'doc': "photon enable status for maia (datasource)"
        },
        'pileuprejectionenable': {
            'default': None,
            'doc': "pileup rejection enable status for maia (datasource)"
        },
        'pixelenable': {
            'default': None,
            'doc': "pixel enable status for maia (datasource)"
        },
        'throttleenable': {
            'default': None,
            'doc': "throttle enable status for maia (datasource)"
        },
    },
    'pointdet': {
        'data': {
            'default': None,
            'doc': "diode data (datasource)"
        },
        'detname': {
            'default': 'detector',
            'doc': "detector group name (string)"
        },
    },
    'maiaflux': {
        'detname': {
            'default': "maia",
            'doc': "detector (alias) name (string)"
        },
        'fname': {
            'default': "fluxdevice",
            'doc': "flux name group (string)"
        },
        'fluxname': {
            'default': None,
            'doc': "flux name for maia (datasource)"
        },
        'unit': {
            'default': None,
            'doc': "flux unit for maia (datasource)"
        },
        'source': {
            'default': None,
            'doc': "flux source for maia (datasource)"
        },
        'coefficient': {
            'default': None,
            'doc': "flux coefficient  for maia (datasource)"
        },
        'vfcfactor': {
            'default': None,
            'doc': "vfc conversion factor (datasource)"
        },
        'keithleydevice': {
            'default': "keithley",
            'doc': "keithley device name (string)"
        },
    },
    'maiadimension': {
        'detname': {
            'default': "maia",
            'doc': "detector (alias) name (string)"
        },
        'dname': {
            'default': "dimension",
            'doc': "dimension name group (string)"
        },
        'dimname': {
            'default': None,
            'doc': "dimension name for maia (datasource)"
        },
        'positionsource': {
            'default': None,
            'doc': "position source of dimension for maia (datasource)"
        },
        'pixelpitch': {
            'default': None,
            'doc': "pixel pitch of dimension for maia (datasource)"
        },
        'origin': {
            'default': None,
            'doc': "pixel origin of dimension for maia (datasource)"
        },
        'hysteresis': {
            'default': None,
            'doc': "pixel hysteresis of dimension for maia (datasource)"
        },
        'unit': {
            'default': None,
            'doc': "position units of dimension for maia (datasource)"
        },
        'numberofpixels': {
            'default': None,
            'doc': "number of pixels of dimension for maia (datasource)"
        },
    },
    'chcut': {
        'usage': {
            'default': 'Bragg',
            'doc': "the crystall usage, e.g. Laue (string)"
        },
        'energy': {
            'default': None,
            'doc': "synchronized monochromator energy (datasource)"
        },
        'reflection': {
            'default': None,
            'doc': "reflection from string (datasource)"
        },
        'energyfmb': {
            'default': None,
            'doc': "monochromator energy (datasource)"
        },
        'lat': {
            'default': None,
            'doc': "horizontal lattice translation of the first cristal"
            " (datasource)"
        },
        'latname': {
            'default': 'lat',
            'doc': "horizontal lattice translation name of the first cristal"
            " (string)"
        },
        'yaw': {
            'default': None,
            'doc': "phi rotation of the first cristal"
            " (datasource)"
        },
        'yawname': {
            'default': 'phi',
            'doc': "phi rotation name of the first cristal"
            " (string)"
        },
        'para': {
            'default': None,
            'doc': "distance between the crystals"
            " (string)"
        },
        'paraname': {
            'default': 'para',
            'doc': "beam parallel translation name of the second cristal"
            " (string)"
        },
        'braggangle': {
            'default': None,
            'doc': "bragg angle"
            " (datasource)"
        },
        'bragganglename': {
            'default': 'bragg',
            'doc': "bragg angle name "
            " (string)"
        },
        'jack1': {
            'default': None,
            'doc': "first vertical jack of table"
            " (datasource)"
        },
        'jack1name': {
            'default': 'jack1',
            'doc': "first vertical jack name of table"
            " (string)"
        },
        'jack2': {
            'default': None,
            'doc': "second vertical jack of table"
            " (datasource)"
        },
        'jack2name': {
            'default': 'jack2',
            'doc': "second vertical jack name of table"
            " (string)"
        },
        'jack3': {
            'default': None,
            'doc': "third vertical jack of table"
            " (datasource)"
        },
        'jack3name': {
            'default': 'jack3',
            'doc': "third vertical jack name of table"
            " (string)"
        },
        'table': {
            'default': None,
            'doc': "vertical position of table"
            " (datasource)"
        },
        'tablename': {
            'default': 'table',
            'doc': "vertical position name of table"
            " (string)"
        },
        'oxfordhorizontal': {
            'default': None,
            'doc': " horizontal translation"
            " (datasource)"
        },
        'unitcalibration': {
            'default': None,
            'doc': " unit calibration from dcmmotor"
            " (datasource)"
        },
        'crystal': {
            'default': None,
            'doc': " type of crystal i.e. 0->Si111,1->Si311,2->Si111"
            " ChannelCut  (datasource)"
        },
        'theta': {
            'default': None,
            'doc': "theta angle"
            " (datasource)"
        },
        'thetaname': {
            'default': 'theta',
            'doc': "theta angle name"
            " (string)"
        },
        'chcutdevice': {
            'default': None,
            'doc': "FMBOxfDCMEnergy tango device name"
            " (string)"
        },
    },
    'pinhole': {
        'diameter': {
            'default': None,
            'doc': "pinhole diameter (datasource)"
        },
        'x': {
            'default': None,
            'doc': "horizontal position (datasource)"
        },
        'y': {
            'default': None,
            'doc': "vertical position (datasource)"
        },
        'z': {
            'default': None,
            'doc': "along the beam position (datasource)"
        },
        'xname': {
            'default': 'x',
            'doc': "horizontal position name (string)"
        },
        'yname': {
            'default': 'y',
            'doc': "vertical position name (string)"
        },
        'zname': {
            'default': 'z',
            'doc': "along the beam position name (string)"
        },
        'xsign': {
            'default': "",
            'doc': "horizontal position sign, e.g. '-' (string)"
        },
    },
    'beamstop': {

        'description': {
            'default': 'circular',
            'doc': " circular or  rectangular (string)"
        },
        'x': {
            'default': None,
            'doc': "horizontal position (datasource)"
        },
        'xsign': {
            'default': "",
            'doc': "horizontal position sign, e.g. '-' (string)"
        },
        'y': {
            'default': None,
            'doc': "vertical position (datasource)"
        },
        'z': {
            'default': None,
            'doc': "vertical position (datasource)"
        },
        'xname': {
            'default': 'x',
            'doc': "horizontal position name (string)"
        },
        'yname': {
            'default': 'y',
            'doc': "vertical position name (string)"
        },
        'zname': {
            'default': 'z',
            'doc': "along the beam position name (string)"
        },
    },
    'samplehkl': {
        'sname': {
            'default': 'sample',
            'doc': "sample group name (string)"
        },
        'psi': {
            'default': None,
            'doc': "psi angle position of analyzer (datasource)"
        },
        'h': {
            'default': None,
            'doc': "h position in hkl space (datasource)"
        },
        'k': {
            'default': None,
            'doc': "k position in hkl space (datasource)"
        },
        'l': {
            'default': None,
            'doc': "l position in hkl space (datasource)"
        },
    },
    'absorber': {
        'y': {
            'default': None,
            'doc': "vertical position (datasource)"
        },
        'yname': {
            'default': 'y',
            'doc': "vertical position name (string)"
        },
        'attenfactor': {
            'default': None,
            'doc': "attenuation factor (datasource)"
        },
        'position': {
            'default': None,
            'doc': "which sliders are in [bitarray] MANDATORY (datasource)"
        },
        'foil': {
            'default': None,
            'doc': "foil type, i.e. standard <cpname>_foil (datasource)"
        },
        'thickness': {
            'default': None,
            'doc': "foil thickness, i.e. standard <cpname>_thickness "
            "(datasource)"
        },
        'foillist': {
            'default': '["Ag", "Ag", "Ag", "Ag", "", "Al", "Al", "Al", "Al"]',
            'doc': "foil_type position json dictionary (string)"
        },
        'thicknesslist': {
            'default': '[0.5, 0.05, 0.025, 0.0125, 0, 0.1, 0.3, 0.5, 1.0]',
            'doc': "foil_type position json dictionary (string)"
        },
        'distance': {
            'default': None,
            'doc': "distance for the sample in m, e.g. 0 (string)"
        },
        'distancename': {
            'default': 'distance',
            'doc': "distance name for the sample in m, e.g. 0 (string)"
        },
        'distanceoffset': {
            'default': None,
            'doc': "3-vector distance offset in m, e.g. sample-source "
            "offset if the distance is taken from the source (string)"
        },
        'dependstop': {
            'default': None,
            'doc': "the first transformation, e.g. distance (string)"
        },
        'transformations': {
            'default': None,
            'doc': "transformations group name i.e. 'transformations'. "
            "If it is  not set it is not created (string)"
        },
    },
    'keithley': {
        'gain': {
            'default': None,
            'doc': "gain in V/A (datasource)"
        },
        'risetime': {
            'default': None,
            'doc': "rise time (datasource)"
        },
        'current': {
            'default': None,
            'doc': "current in A (datasource)"
        },
        'voltage': {
            'default': None,
            'doc': "voltage in V (datasource)"
        },
        'sourvoltlevel': {
            'default': None,
            'doc': "source voltage level in V (datasource)"
        },
    },
    'qbpm': {
        'foil': {
            'default': None,
            'doc': "foil type, i.e. standard <cpname>_foil (datasource)"
        },
        'foilpos': {
            'default': None,
            'doc': "foil position MANDATORY (datasource)"
        },
        'x': {
            'default': None,
            'doc': "horizontal position (datasource)"
        },
        'y': {
            'default': None,
            'doc': "vertical position (datasource)"
        },
        'xname': {
            'default': 'x',
            'doc': "horizontal position name (string)"
        },
        'yname': {
            'default': 'y',
            'doc': "vertical position name (string)"
        },
        'foilposdict': {
            'default': '{"Ti": 43, "Ni": 23, "Out": 3}',
            'doc': "foil_type position json dictionary (string)"
        },
        'distance': {
            'default': None,
            'doc': "distance for the sample in m, e.g. 0 (string)"
        },
        'distancename': {
            'default': 'distance',
            'doc': "distance name for the sample in m, e.g. 0 (string)"
        },
        'distanceoffset': {
            'default': None,
            'doc': "3-vector distance offset in m, e.g. sample-source "
            "offset if the distance is taken from the source (string)"
        },
        'dependstop': {
            'default': "x",
            'doc': "the first transformation, e.g. distance (string)"
        },
        'dependsony': {
            'default': "",
            'doc': "the  depends_on y field value,  e.g. distance (string)"
        },
    },
    'slit': {
        'xgap': {
            'default': None,
            'doc': "horizontal gap (datasource)"
        },
        'ygap': {
            'default': None,
            'doc': "vertical gap (datasource)"
        },
        'xoffset': {
            'default': None,
            'doc': "horizontal offset (datasource)"
        },
        'yoffset': {
            'default': None,
            'doc': "vertiacal offset (datasource)"
        },
        'xoffsetname': {
            'default': "x_offset",
            'doc': "horizontal offset name (string)"
        },
        'yoffsetname': {
            'default': "y_offset",
            'doc': "vertiacal offset name (string)"
        },
        'left': {
            'default': None,
            'doc': "left blade position (datasource)"
        },
        'right': {
            'default': None,
            'doc': "right blade position (datasource)"
        },
        'bottom': {
            'default': None,
            'doc': "bottom blade position (datasource)"
        },
        'top': {
            'default': None,
            'doc': "top blade position (datasource)"
        },
        'leftclosed': {
            'default': None,
            'doc': "left blade closed position (datasource)"
        },
        'rightclosed': {
            'default': None,
            'doc': "right blade closed position (datasource)"
        },
        'bottomclosed': {
            'default': None,
            'doc': "bottom blade closed position (datasource)"
        },
        'topclosed': {
            'default': None,
            'doc': "top blade closed position (datasource)"
        },
        'xoffsetcalibration': {
            'default': None,
            'doc': "horizontal offset calibration (datasource)"
        },
        'yoffsetcalibration': {
            'default': None,
            'doc': "vertiacal offset calibration (datasource)"
        },
        'xoffsetcalibrationname': {
            'default': "x_offset_calibration",
            'doc': "horizontal offset calibration name (string)"
        },
        'yoffsetcalibrationname': {
            'default': "y_offset_calibration",
            'doc': "vertiacal offset calibration name (string)"
        },
        'distance': {
            'default': None,
            'doc': "distance for the sample in m, e.g. 0 (string)"
        },
        'distancename': {
            'default': "distance",
            'doc': "distance name for the sample in m, e.g. 0 (string)"
        },
        'distanceoffset': {
            'default': None,
            'doc': "3-vector distance offset in m, e.g. sample-source"
            " offset if the distance is taken from the source (string)"
        },
        'dependstop': {
            'default': None,
            'doc': "the first transformation, e.g. distance (string)"
        },
        'yoffdependson': {
            'default': 'distance',
            'doc': "the first transformation, e.g. distance (string)"
        },
        'xoffdependson': {
            'default': 'y_offset',
            'doc': "the first transformation, e.g. distance (string)"
        },
        'transformations': {
            'default': None,
            'doc': "transformations group name i.e. 'transformations'. "
            "If it is  not set it is not created (string)"
        },
    },
    'source': {
        'srcname': {
            'default': 'source',
            'doc': "source group name (string)"
        },
        'beamcurrent': {
            'default': None,
            'doc': "ring beam current (datasource)"
        },
        'sourceenergy': {
            'default': None,
            'doc': "ring beam energy (datasource)"
        },
        'numberofbunches': {
            'default': None,
            'doc': "number of source bunches (datasource)"
        },
        'bunchmode': {
            'default': 'Multi Bunch',
            'doc': "bunch mode (string)"
        },
    },
    'undulator': {
        'uname': {
            'default': 'insertion_device',
            'doc': "insertion_device group name (string)"
        },
        'energy': {
            'default': None,
            'doc': "undulator energy (datasource)"
        },
        'gap': {
            'default': None,
            'doc': "separation between opposing pairs of magnetic pole"
            " (datasource)"
        },
        'shift': {
            'default': None,
            'doc': "undulator shift"
            " (datasource)"
        },
        'speed': {
            'default': None,
            'doc': "undulator speed"
            " (datasource)"
        },
        'gapunits': {
            'default': 'mm',
            'doc': "gap units"
            " (string)"
        },
        'taperunits': {
            'default': 'mm',
            'doc': "gap units"
            " (string)"
        },
        'shiftunits': {
            'default': 'mm',
            'doc': "shift units"
            " (string)"
        },
        'speedunits': {
            'default': '',
            'doc': "speed units"
            " (string)"
        },
        'taper': {
            'default': None,
            'doc': "gap difference between upstream and downstream ends"
            " of the insertion device (datasource)"
        },
        'harmonic': {
            'default': None,
            'doc': "undulator harmonic (datasource)"
        },
        'type': {
            'default': "undulator",
            'doc': "undulator or wiggler (string)"
        },
        'length': {
            'default': "2",
            'doc': "length of insertion device in meters (string)"
        },
        'distance': {
            'default': None,
            'doc': "distance from the sample in m, e.g. 0 (string)"
        },
        'distancename': {
            'default': "distance",
            'doc': "distance name from the sample in m, e.g. 0 (string)"
        },
        'distanceoffset': {
            'default': None,
            'doc': "3-vector distance offset in m, e.g. sample-source offset "
            "if the distance is taken from the source (string)"
        },
        'dependstop': {
            'default': None,
            'doc': "the first transformation, e.g. distance (string)"
        },
        'transformations': {
            'default': None,
            'doc': "transformations group name i.e. 'transformations'. "
            "If it is  not set it is not created (string)"
        },
    },
    'beamtimeid': {
        'shortname': {
            'default': "P09",
            'doc': "beamline short name (string)"
        },
        'currentdir': {
            'default': "/gpfs/current",
            'doc': "beamtime file directory (string)"
        },
        'localdir': {
            'default': "/gpfs/local",
            'doc': "local file directory (string)"
        },
        'currentprefix': {
            'default': "beamtime-metadata-",
            'doc': "beamtime file prefix (string)"
        },
        'currentpostfix': {
            'default': ".txt",
            'doc': "beamtime file postfix (string)"
        },
        'commissiondir': {
            'default': "/gpfs/commissioning",
            'doc': "commission file directory (string)"
        },
        'commissionprefix': {
            'default': "commissioning-metadata-",
            'doc': "commission file prefix (string)"
        },
        'commissionpostfix': {
            'default': ".txt",
            'doc': "commission file postfix (string)"
        },
    },
    'default': {
        'control': {
            'default': None,
            'doc': "group name of the monitor (string)"
        },
        'shortname': {
            'default': "P09",
            'doc': "beamline short name (string)"
        },
        'longname': {
            'default': "P09 Resonant Scattering and Diffraction beamline",
            'doc': "beamline long name (string)"
        },
        'sourcename': {
            'default': "PETRA III",
            'doc': "source name (string)"
        },
        '__tangohost__': {
            'default': "localhost",
            'doc': "tango host (string)"
        },
        '__tangoport__': {
            'default': "10000",
            'doc': "tango port (string)"
        },
        '__configdevice__': {
            'default': "nxs/configserver/localhost",
            'doc': "configuration server device name (string)"
        },
        'srcname': {
            'default': 'source',
            'doc': "source group name (string)"
        },
    },
    'datasignal': {
        'signal': {
            'default': 'signalname',
            'doc': "data signal field name (string)"
        },
        'axes': {
            'default': None,
            'doc': "data axes field name(s) (string)"
        },
    },
    'defaultinstrument': {
        'control': {
            'default': None,
            'doc': "group name of the monitor (string)"
        },
        'shortname': {
            'default': "P09",
            'doc': "beamline short name (string)"
        },
        'longname': {
            'default': "P09 Resonant Scattering and Diffraction beamline",
            'doc': "beamline long name (string)"
        },
        'sourcename': {
            'default': "PETRA III",
            'doc': "source name (string)"
        },
        '__tangohost__': {
            'default': "localhost",
            'doc': "tango host (string)"
        },
        '__tangoport__': {
            'default': "10000",
            'doc': "tango port (string)"
        },
        '__configdevice__': {
            'default': "nxs/configserver/localhost",
            'doc': "configuration server device name (string)"
        },
        'srcname': {
            'default': 'source',
            'doc': "source group name (string)"
        },
    },
    'defaultsample': {
    },
    'dcm': {
        'usage': {
            'default': 'Bragg',
            'doc': "the crystall usage, e.g. Laue (string)"
        },
        'topdependson2': {
            'default': 'chi',
            'doc': "the first transformation of the second crystal,"
            " e.g. lat (string)"
        },
        'phi1dependson': {
            'default': '../../transformations/bragg',
            'doc': "the depends_on field of the first cristal phi, "
            "e.g. theta (string)"
        },
        'chi2dependson': {
            'default': 'theta',
            'doc': "the depends_on field of the second cristal chi, "
            "e.g. phi (string)"
        },
        'bend1': {
            'default': None,
            'doc': "bending of the first cristal"
            " (datasource)"
        },
        'bend2': {
            'default': None,
            'doc': "bending of the second cristal"
            " (datasource)"
        },
        'energy': {
            'default': None,
            'doc': "synchronized monochromator energy (datasource)"
        },
        'energyfmb': {
            'default': None,
            'doc': "monochromator energy (datasource)"
        },
        'lat': {
            'default': None,
            'doc': "horizontal lattice translation of the first cristal"
            " (datasource)"
        },
        'latname': {
            'default': 'lat',
            'doc': "horizontal lattice translation name of the first cristal"
            " (string)"
        },
        'lat2': {
            'default': None,
            'doc': "horizontal lattice translation of the second cristal"
            " (datasource)"
        },
        'lat2name': {
            'default': 'lat',
            'doc': "horizontal lattice translation name of the second cristal"
            " (string)"
        },
        'yaw': {
            'default': None,
            'doc': "phi rotation of the first cristal"
            " (datasource)"
        },
        'yawname': {
            'default': 'phi',
            'doc': "phi rotation name of the first cristal"
            " (string)"
        },
        'yaw2': {
            'default': None,
            'doc': "phi rotation of the second cristal"
            " (datasource)"
        },
        'yaw2name': {
            'default': 'phi',
            'doc': "phi rotation name of the second cristal"
            " (string)"
        },
        'roll1': {
            'default': None,
            'doc': "chi rotation of the first cristal"
            " (datasource)"
        },
        'roll1name': {
            'default': 'chi',
            'doc': "chi rotation name of the first cristal"
            " (string)"
        },
        'roll2': {
            'default': None,
            'doc': "chi rotation of the second cristal"
            " (datasource)"
        },
        'roll2name': {
            'default': 'chi',
            'doc': "chi rotation name of the second cristal"
            " (string)"
        },
        'pitch1': {
            'default': None,
            'doc': "theta rotation of the first cristal"
            " (datasource)"
        },
        'pitch1name': {
            'default': 'theta',
            'doc': "theta rotation name of the first cristal"
            " (string)"
        },
        'pitch2': {
            'default': None,
            'doc': "theta rotation of the second cristal"
            " (datasource)"
        },
        'pitch2name': {
            'default': 'theta',
            'doc': "theta rotation name of the second cristal"
            " (string)"
        },
        'perp2': {
            'default': None,
            'doc': "vertical translation of the second cristal"
            " (datasource)"
        },
        'perp2name': {
            'default': 'perp',
            'doc': "vertical translation name of the second cristal"
            " (string)"
        },
        'par2': {
            'default': None,
            'doc': "beam parallel translation of the second cristal"
            " (datasource)"
        },
        'par2name': {
            'default': 'para',
            'doc': "beam parallel translation name of the second cristal"
            " (string)"
        },
        'braggangle': {
            'default': None,
            'doc': "bragg angle"
            " (datasource)"
        },
        'bragganglename': {
            'default': 'bragg',
            'doc': "bragg angle name "
            " (string)"
        },
        'jack1': {
            'default': None,
            'doc': "first vertical jack of table"
            " (datasource)"
        },
        'jack1name': {
            'default': 'jack1',
            'doc': "first vertical jack name of table"
            " (string)"
        },
        'jack2': {
            'default': None,
            'doc': "second vertical jack of table"
            " (datasource)"
        },
        'jack2name': {
            'default': 'jack2',
            'doc': "second vertical jack name of table"
            " (string)"
        },
        'jack3': {
            'default': None,
            'doc': "third vertical jack of table"
            " (datasource)"
        },
        'jack3name': {
            'default': 'jack3',
            'doc': "third vertical jack name of table"
            " (string)"
        },
        'table': {
            'default': None,
            'doc': "vertical position of table"
            " (datasource)"
        },
        'tablename': {
            'default': 'table',
            'doc': "vertical position name of table"
            " (string)"
        },
        'oxfordhorizontal': {
            'default': None,
            'doc': " horizontal translation"
            " (datasource)"
        },
        'unitcalibration': {
            'default': None,
            'doc': "unit calibration from dcmmotor"
            " (datasource)"
        },
        'crystal': {
            'default': None,
            'doc': "type of crystal i.e. 0->Si111,1->Si311,2->Si111 ChannelCut"
            " (datasource)"
        },
        'exitoffset': {
            'default': None,
            'doc': " exit offset"
            " (datasource)"
        },
        'theta': {
            'default': None,
            'doc': "theta angle"
            " (datasource)"
        },
        'thetaname': {
            'default': 'theta',
            'doc': "theta angle name"
            " (string)"
        },
        'dcmdevice': {
            'default': None,
            'doc': "FMBOxfDCMEnergy tango device"
            " (string)"
        },
    },
    'collect2': {
        'first': {
            'default': None,
            'doc': "name of the first component to collect MANDATORY"
            " (datasource)"
        },
        'second': {
            'default': None,
            'doc': "name of the second component to collect MANDATORY"
            " (datasource)"
        }
    },
    'collect3': {
        'first': {
            'default': None,
            'doc': "name of the first component to collect MANDATORY"
            " (datasource)"
        },
        'second': {
            'default': None,
            'doc': "name of the second component to collect MANDATORY"
            " (datasource)"
        },
        'third': {
            'default': None,
            'doc': "name of the third component to collect MANDATORY"
            " (datasource)"
        }
    },
    'collect4': {
        'first': {
            'default': None,
            'doc': "name of the first component to collect MANDATORY"
            " (datasource)"
        },
        'second': {
            'default': None,
            'doc': "name of the second component to collect MANDATORY"
            " (datasource)"
        },
        'third': {
            'default': None,
            'doc': "name of the third component to collect MANDATORY"
            " (datasource)"
        },
        'fourth': {
            'default': None,
            'doc': "name of the fourth component to collect MANDATORY"
            " (datasource)"
        }
    },
    'collect5': {
        'first': {
            'default': None,
            'doc': "name of the first component to collect MANDATORY"
            " (datasource)"
        },
        'second': {
            'default': None,
            'doc': "name of the second component to collect MANDATORY"
            " (datasource)"
        },
        'third': {
            'default': None,
            'doc': "name of the third component to collect MANDATORY"
            " (datasource)"
        },
        'fourth': {
            'default': None,
            'doc': "name of the fourth component to collect MANDATORY"
            " (datasource)"
        },
        'fifth': {
            'default': None,
            'doc': "name of the fifth component to collect MANDATORY"
            " (datasource)"
        }
    },
    'collect6': {
        'first': {
            'default': None,
            'doc': "name of the first component to collect MANDATORY"
            " (datasource)"
        },
        'second': {
            'default': None,
            'doc': "name of the second component to collect MANDATORY"
            " (datasource)"
        },
        'third': {
            'default': None,
            'doc': "name of the third component to collect MANDATORY"
            " (datasource)"
        },
        'fourth': {
            'default': None,
            'doc': "name of the fourth component to collect MANDATORY"
            " (datasource)"
        },
        'fifth': {
            'default': None,
            'doc': "name of the fifth component to collect MANDATORY"
            " (datasource)"
        },
        'sixth': {
            'default': None,
            'doc': "name of the sixth component to collect MANDATORY"
            " (datasource)"
        }
    },
    'common2': {
        'dds': {
            'default': None,
            'doc': "default read datasource name MANDATORY (datasource)"
        },
        'ods': {
            'default': None,
            'doc': "optional detasource name MANDATORY (datasource)"
        }
    },
    'mssar': {
        'msenv': {
            'default': None,
            'doc': "sardana environment (datasource)"
        },
        'varname': {
            'default': None,
            'doc': "sardana environment variable name MANDATORY (string)"
        },
        'mssardanadevice': {
            'default': None,
            'doc': "macroserver sardana device name MANDATORY (string)"
        },
        '__tangohost__': {
            'default': "localhost",
            'doc': "tango host (string)"
        },
        '__tangoport__': {
            'default': "10000",
            'doc': "tango port (string)"
        },
    },
    'msnsar': {
        'msenv': {
            'default': None,
            'doc': "sardana environment (datasource)"
        },
        'varname': {
            'default': None,
            'doc': "nested sardana environment variable name "
            " MANDATORY (string)"
        },
        'mssardanadevice': {
            'default': None,
            'doc': "sardana device name MANDATORY (string)"
        },
        '__tangohost__': {
            'default': "localhost",
            'doc': "tango host (string)"
        },
        '__tangoport__': {
            'default': "10000",
            'doc': "tango port (string)"
        },
    },
    'common3': {
        'dds': {
            'default': None,
            'doc': "default read datasource name MANDATORY (datasource)"
        },
        'ods1': {
            'default': None,
            'doc': "fist optional detasource name MANDATORY (datasource)"
        },
        'ods2': {
            'default': None,
            'doc': "second optional detasource name MANDATORY (datasource)"
        }
    },
}

#: (:obj:`dict` <:obj:`str` , :obj:`list` <:obj:`str`> >)
#:     xml template files of modules
standardComponentTemplateFiles = {
    'qbpm': [
        'qbpm_foil.ds.xml',
        'qbpm.xml',
    ],
    'slit': ['slit.xml'],
    'source': ['source.xml'],
    'undulator': ['undulator.xml'],
    'beamtimeid': [
        'beamtimeid.xml',
        'beamtimeid.ds.xml',
        'start_time.ds.xml',
    ],
    'default': [
        'default.xml',
        'defaultsample.xml',
        'defaultinstrument.xml',
        'sample_name.ds.xml',
        'chemical_formula.ds.xml',
        'beamtime_id.ds.xml',
        'start_time.ds.xml',
        'end_time.ds.xml',
        'nexdatas_version.ds.xml',
        'nexdatas_configuration.ds.xml',
        'title.ds.xml',
    ],
    'defaultsample': [
        'defaultsample.xml',
        'sample_name.ds.xml',
        'chemical_formula.ds.xml',
    ],
    'datasignal': [
        'datasignal.xml',
        'signal_name.ds.xml',
        'signalname.ds.xml',
        'signal_axes.ds.xml',
    ],
    'defaultinstrument': [
        'defaultinstrument.xml',
        'beamtime_id.ds.xml',
        'start_time.ds.xml',
        'end_time.ds.xml',
        'nexdatas_version.ds.xml',
        'nexdatas_configuration.ds.xml',
        'title.ds.xml',
    ],
    'dcm': [
        'dcm.xml',
        'dcm_reflection.ds.xml',
        'dcm_unitcalibration.ds.xml',
        'dcm_crystal.ds.xml',
    ],
    'chcut': [
        'chcut.xml',
        'chcut_unitcalibration.ds.xml',
        'chcut_crystal.ds.xml',
    ],
    'empty': [
        'empty.xml',
    ],
    'maia': [
        'maia.xml',
        'empty.xml',
    ],
    'maiadimension': [
        'maiadimension.xml',
    ],
    'maiaflux': [
        'maiaflux.xml',
    ],
    'collect2': [
        'collect2.xml',
    ],
    'collect3': [
        'collect3.xml',
    ],
    'collect4': [
        'collect4.xml',
    ],
    'collect5': [
        'collect5.xml',
    ],
    'collect6': [
        'collect6.xml',
    ],
    'common2': [
        'common2_common.ds.xml',
    ],
    'common3': [
        'common3_common.ds.xml',
    ],
    'msnsar': [
        'msnsar_env.ds.xml',
        'sardanaenvironment.ds.xml',
    ],
    'mssar': [
        'mssar_env.ds.xml',
        'sardanaenvironment.ds.xml',
    ],
    'absorber': [
        'absorber_foil.ds.xml',
        'absorber_thickness.ds.xml',
        'absorber.xml',
    ],
    'keithley': [
        'keithley.xml',
    ],
    'pinhole': [
        'pinhole.xml',
    ],
    'beamstop': [
        'beamstop.xml',
    ],
    'samplehkl': [
        'samplehkl.xml'
    ],
    'pointdet': [
        'pointdet.xml',
    ],
}

#: (:obj:`dict` <:obj:`str` , :obj:`list` <:obj:`str`> >)
#:     xml template files of modules
moduleTemplateFiles = {
    'mythen2': ['mythen2.xml'],
    'mythen': ['mythen.xml',
               'mythen_postrun.ds.xml',
               'mythen_filestartnumber.ds.xml'],
    'pilatus100k': ['pilatus.xml',
                    'pilatus_postrun.ds.xml',
                    'pilatus100k_description.ds.xml',
                    'pilatus_mxparameters_cb.ds.xml',
                    'pilatus_filestartnum_cb.ds.xml'],
    'pilatus300k': ['pilatus.xml',
                    'pilatus_postrun.ds.xml',
                    'pilatus300k_description.ds.xml',
                    'pilatus_mxparameters_cb.ds.xml',
                    'pilatus_filestartnum_cb.ds.xml'],
    'pilatus1m': ['pilatus.xml',
                  'pilatus_postrun.ds.xml',
                  'pilatus1m_description.ds.xml',
                  'pilatus_mxparameters_cb.ds.xml',
                  'pilatus_filestartnum_cb.ds.xml'],
    'pilatus2m': ['pilatus.xml',
                  'pilatus_postrun.ds.xml',
                  'pilatus6m_description.ds.xml',
                  'pilatus_mxparameters_cb.ds.xml',
                  'pilatus_filestartnum_cb.ds.xml'],
    'pilatus6m': ['pilatus.xml',
                  'pilatus_postrun.ds.xml',
                  'pilatus_mxparameters_cb.ds.xml',
                  'pilatus6m_description.ds.xml',
                  'pilatus_filestartnum_cb.ds.xml'],
    'pilatus': ['pilatus.xml',
                'pilatus_postrun.ds.xml',
                'pilatus_description.ds.xml',
                'pilatus_mxparameters_cb.ds.xml',
                'pilatus_filestartnum_cb.ds.xml'],
    'limaccd': ['limaccd.xml',
                'limaccd_postrun.ds.xml',
                'limaccd_xpixelsize.ds.xml',
                'limaccd_ypixelsize.ds.xml',
                'limaccd_description.ds.xml',
                'limaccd_filestartnum_cb.ds.xml'],
    'limaccds': ['limaccd.xml',
                 'limaccd_postrun.ds.xml',
                 'limaccd_xpixelsize.ds.xml',
                 'limaccd_ypixelsize.ds.xml',
                 'limaccd_description.ds.xml',
                 'limaccd_filestartnum_cb.ds.xml'],
    'pco': ['pco.xml',
            'pco_postrun.ds.xml',
            'pco_description.ds.xml',
            'pco_filestartnum_cb.ds.xml'],
    'pcoedge': ['pco.xml',
                'pco_postrun.ds.xml',
                'pco_description.ds.xml',
                'pco_filestartnum_cb.ds.xml'],
    'pco4000': ['pco.xml',
                'pco_postrun.ds.xml',
                'pco_description.ds.xml',
                'pco_filestartnum_cb.ds.xml'],
    'lambda': ['lambda.xml',
               'lambda_nxdata.ds.xml',
               'lambda_external_data.ds.xml'],
    'tangovimba': ['tangovimba.xml',
                   'tangovimba_nxdata.ds.xml',
                   'tangovimba_external_data.ds.xml'],
    'lambda2m': ['lambda2m.xml',
                 'lambda2m_m1_nxdata.ds.xml',
                 'lambda2m_m2_nxdata.ds.xml',
                 'lambda2m_m3_nxdata.ds.xml',
                 'lambda2m_m1_external_data.ds.xml',
                 'lambda2m_m2_external_data.ds.xml',
                 'lambda2m_m3_external_data.ds.xml'],
    'perkinelmerdetector': [
        'perkinelmerdetector.xml',
        'perkinelmerdetector_postrun.ds.xml',
        'perkinelmerdetector_description.ds.xml',
        'perkinelmerdetector_fileindex_cb.ds.xml'
    ],
    'perkinelmer': [
        'perkinelmerdetector.xml',
        'perkinelmerdetector_postrun.ds.xml',
        'perkinelmerdetector_description.ds.xml',
        'perkinelmerdetector_fileindex_cb.ds.xml'
    ],
    'pedetector': [
        'perkinelmerdetector.xml',
        'perkinelmerdetector_postrun.ds.xml',
        'perkinelmerdetector_description.ds.xml',
        'perkinelmerdetector_fileindex_cb.ds.xml'
    ],
    'marccd': ['marccd.xml',
               'marccd_postrun.ds.xml'],
    'mca_xia': [
        'mcaxia.xml'
    ],
    'eigerdectris': [
        'eigerdectris.xml',
        'eigerdectris_stepindex.ds.xml',
        'eigerdectris_description_cb.ds.xml',
        'eigerdectris_triggermode_cb.ds.xml'
    ],
}

#: (:obj:`dict` <:obj:`str` , :obj:`list` <:obj:`str`> >)
#:     important attributes of modules
moduleMultiAttributes = {
    'mca_xia': [
        'ICR', 'OCR',
    ],
    'mca_xia@pool': [
        'CountsRoI', 'RoIEnd', 'RoIStart',
    ],
    'limaccd': [
        'camera_type', 'camera_pixelsize', 'camera_model',
        'acq_mode', 'acq_nb_frames', 'acq_trigger_mode',
        'last_image_saved',
        'latency_time',  'acc_max_expo_time',
        'acc_expo_time', 'acc_time_mode',
        'acc_dead_time', 'acc_live_time',
        'saving_mode',
        'saving_directory',
        'saving_prefix',
        'saving_suffix',
        'saving_next_number',
        'saving_format',
        'saving_frame_per_file',
        'image_type',
        'image_width',
        'image_height',
        'image_sizes',
        'image_roi',
        'image_bin',
        'image_flip',
        'image_rotation',
        'shutter_mode',
        'shutter_open_time',
    ],
    'limaccds': [
        'camera_type', 'camera_pixelsize', 'camera_model',
        'acq_mode', 'acq_nb_frames', 'acq_trigger_mode',
        'last_image_saved',
        'latency_time', 'acc_max_expo_time',
        'acc_expo_time',  'acc_time_mode',
        'acc_dead_time', 'acc_live_time',
        'saving_mode',
        'saving_directory',
        'saving_prefix',
        'saving_suffix',
        'saving_next_number',
        'saving_format',
        'saving_frame_per_file',
        'image_type',
        'image_width',
        'image_height',
        'image_sizes',
        'image_roi',
        'image_bin',
        'image_flip',
        'image_rotation',
        'shutter_mode',
        'shutter_open_time',
    ],
    'pco': [
        'DelayTime', 'ExposureTime', 'NbFrames', 'TriggerMode',
        'FileDir', 'FilePostfix', 'FilePrefix', 'FileStartNum',
        'Binning_x', 'Binning_y', 'ROI_x_min', 'ROI_x_max',
        'ROI_y_min', 'ROI_y_max', 'Pixelrate', 'ADCs',
        'CoolingTemp', 'CoolingTempSet', 'ImageTimeStamp',
        'RecorderMode',
    ],
    'pcoedge': [
        'DelayTime', 'ExposureTime', 'NbFrames', 'TriggerMode',
        'FileDir', 'FilePostfix', 'FilePrefix', 'FileStartNum',
        'Binning_x', 'Binning_y', 'ROI_x_min', 'ROI_x_max',
        'ROI_y_min', 'ROI_y_max', 'Pixelrate', 'ADCs',
        'CoolingTemp', 'CoolingTempSet', 'ImageTimeStamp',
        'RecorderMode',
    ],
    'pco4000': [
        'DelayTime', 'ExposureTime', 'NbFrames', 'TriggerMode',
        'FileDir', 'FilePostfix', 'FilePrefix', 'FileStartNum',
        'Binning_x', 'Binning_y', 'ROI_x_min', 'ROI_x_max',
        'ROI_y_min', 'ROI_y_max', 'Pixelrate', 'ADCs',
        'CoolingTemp', 'CoolingTempSet', 'ImageTimeStamp',
        'RecorderMode',
    ],
    'maialogger': ['RunNumber'],
    'maiadimension': ['Name', 'PositionSource', 'PixelPitch', 'PixelOrigin',
                      'PixelHysteresis', 'PositionUnit', 'PixelCoordExtent'],
    'maiasensor': ['BiasVoltage', 'LeakageCurrent',
                   'PeltierCurrent', 'WaterTemperature',
                   'DetectorTemperature', 'MosfetTemperature', 'Identity'],
    'maiaflux': ['FluxCoeff', 'FluxName', 'FluxUnit', 'FluxSource'],
    'maiaprocessing': ['GaintrimEnable', 'LineariseEnable', 'PhotonEnable',
                       'PileupRejectEnable', 'PixelEnable',
                       'ThrottleEnable'],
    'maiainterlock': ['BiasPeltierInterlock', 'BiasPeltierInterlockUptime',
                      'Pressure'],
    'pilatus100k': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'pilatus300k': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'pilatus1m': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'pilatus2m': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'pilatus6m': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'perkinelmerdetector': [
        'BinningMode', 'FileIndex', 'ExposureTime', 'SkippedAtStart',
        'SummedSaveImages', 'SkippedBetweenSaved', 'FilesAfterTrigger',
        'FilesBeforeTrigger', 'SummedDarkImages', 'OutputDirectory',
        'FilePattern', 'FileName', 'LogFile', 'UserComment1', 'CameraGain',
        'UserComment2', 'UserComment3', 'UserComment4', 'SaveRawImages',
        'SaveDarkImages', 'PerformIntegration', 'SaveIntegratedData',
        'SaveSubtracted', 'PerformDarkSubtraction'
    ],
    'perkinelmer': [
        'BinningMode', 'FileIndex', 'ExposureTime', 'SkippedAtStart',
        'SummedSaveImages', 'SkippedBetweenSaved', 'FilesAfterTrigger',
        'FilesBeforeTrigger', 'SummedDarkImages', 'OutputDirectory',
        'FilePattern', 'FileName', 'LogFile', 'UserComment1', 'CameraGain',
        'UserComment2', 'UserComment3', 'UserComment4', 'SaveRawImages',
        'SaveDarkImages', 'PerformIntegration', 'SaveIntegratedData',
        'SaveSubtracted', 'PerformDarkSubtraction'
    ],
    'lambda': [
        'TriggerMode', 'ShutterTime', 'DelayTime', 'FrameNumbers', 'ThreadNo',
        'EnergyThreshold', 'OperatingMode', 'ConfigFilePath', 'SaveAllImages',
        'FilePrefix', 'FileStartNum', 'FilePreExt', 'FilePostfix',
        'SaveFilePath', 'SaveFileName', 'LatestImageNumber', 'LiveMode',
        'TotalLossFrames', 'CompressorShuffle', 'CompressionRate',
        'CompressionEnabled', 'Layout', 'ShutterTimeMax', 'ShutterTimeMin',
        'Width', 'Height', 'Depth', 'LiveFrameNo', 'DistortionCorrection',
        'LiveLastImageData', 'FramesPerFile'
    ],
    'lambda2m': [
        'TriggerMode', 'ShutterTime', 'DelayTime', 'FrameNumbers', 'ThreadNo',
        'EnergyThreshold', 'OperatingMode', 'ConfigFilePath', 'SaveAllImages',
        'FilePrefix', 'FileStartNum', 'FilePreExt', 'FilePostfix',
        'SaveFilePath', 'SaveFileName', 'LatestImageNumber', 'LiveMode',
        'TotalLossFrames', 'CompressorShuffle', 'CompressionRate',
        'CompressionEnabled', 'Layout', 'ShutterTimeMax', 'ShutterTimeMin',
        'Width', 'Height', 'Depth', 'LiveFrameNo', 'DistortionCorrection',
        'LiveLastImageData'
    ],
    'pedetector': [
        'BinningMode', 'FileIndex', 'ExposureTime', 'SkippedAtStart',
        'SummedSaveImages', 'SkippedBetweenSaved', 'FilesAfterTrigger',
        'FilesBeforeTrigger', 'SummedDarkImages', 'OutputDirectory',
        'FilePattern', 'FileName', 'LogFile', 'UserComment1', 'CameraGain',
        'UserComment2', 'UserComment3', 'UserComment4', 'SaveRawImages',
        'SaveDarkImages', 'PerformIntegration', 'SaveIntegratedData',
        'SaveSubtracted', 'PerformDarkSubtraction'
    ],
    'pilatus': [
        'DelayTime', 'ExposurePeriod', 'ExposureTime', 'FileDir',
        'FilePostfix', 'FilePrefix', 'FileStartNum', 'LastImageTaken',
        'NbExposures', 'NbFrames', 'MXparameters'],
    'mythen': [
        'Counts1', 'Counts2', 'CountsMax', 'CountsTotal', 'ExposureTime',
        'FileDir', 'FileIndex', 'FilePrefix', 'Data', 'RoI1', 'RoI2'
    ],
    'mythen2': [
        'Counts1', 'Counts2', 'CountsMax', 'CountsTotal', 'ExposureTime',
        'FileDir', 'FileIndex', 'FilePrefix', 'Data',
        'Energy', 'NbFrames', 'RoI1End', 'RoI2End', 'RoI1Start', 'RoI2Start',
        'Threshold'
    ],
    'marccd': [
        'FrameShift', 'SavingDirectory', 'SavingPostfix', 'SavingPrefix'],
    'eigerdectris': [
        'TriggerMode', 'NbTriggers', 'Description', 'NbImages', 'BitDepth',
        'ReadoutTime', 'CountTime', 'EnergyThreshold', 'FrameTime',
        'RateCorrectionEnabled', 'FlatFieldEnabled', 'Temperature',
        'AutoSummationEnabled', 'Humidity', 'PhotonEnergy', 'Wavelength',
    ],
    'tangovimba': [
        'Width', 'WidthMax', 'TriggerSource', 'PixelFormat', 'OffsetY',
        'OffsetX', 'HeightMax', 'Height', 'GainRaw', 'ExposureTimeAbs',
        'AcquisitionFrameRateAbs', 'AcquisitionFrameRateLimit',
        'StreamBytesPerSecond',
        'BinComment', 'FileDir', 'FilePostfix', 'FilePrefix', 'FileSaving',
        'FileStartNum', 'FramesProcessed', 'Image16', 'Image8', 'ImageRaw',
        'MaxLoad', 'ReadMode', 'TuneMode', 'ViewingMode'
    ],
}
