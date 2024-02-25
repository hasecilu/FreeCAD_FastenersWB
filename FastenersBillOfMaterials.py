# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2024                                                    *
*   Alex Neufeld <alex.d.neufeld@gmail.com>                               *
*                                                                         *
*   This file is a supplement to the FreeCAD CAx development system.      *
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU Lesser General Public License (LGPL)    *
*   as published by the Free Software Foundation; either version 2 of     *
*   the License, or (at your option) any later version.                   *
*   for detail see the LICENCE text file.                                 *
*                                                                         *
*   This software is distributed in the hope that it will be useful,      *
*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
*   GNU Library General Public License for more details.                  *
*                                                                         *
*   You should have received a copy of the GNU Library General Public     *
*   License along with this macro; if not, write to the Free Software     *
*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
*   USA                                                                   *
*                                                                         *
***************************************************************************
"""
import os
from collections import defaultdict
import FreeCAD
import FreeCADGui
from TranslateUtils import translate
from FSutils import iconPath
from FastenerBase import FSCommands
from FastenerBase import GetTotalObjectRepeats
from FastenersCmd import FSScrewObject

# fmt: off
fastener_designations = {
    "4PWTI": translate("FastenerBOM", "Tee nut Inserts for wood, {diameter}"),
    "ASMEB18.2.1.1": translate("FastenerBOM", "Square Head Bolts, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.1.6": translate("FastenerBOM", "Hex Cap Screws, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.1.8": translate("FastenerBOM", "Hex Flange Screws, ASME B18.2.1, {diameter} x {length}"),
    "ASMEB18.2.2.1A": translate("FastenerBOM", "Hex Machine Screw Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.1B": translate("FastenerBOM", "Square Machine Screw Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.12": translate("FastenerBOM", "Hex Flange Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.13": translate("FastenerBOM", "Hex Coupling Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.2": translate("FastenerBOM", "Square Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.4A": translate("FastenerBOM", "Hex Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.4B": translate("FastenerBOM", "Hex Jam Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.2.2.5": translate("FastenerBOM", "Hex Slotted Nuts, ASME B18.2.2, {diameter}"),
    "ASMEB18.21.1.12A": translate("FastenerBOM", "Plain Washers, Narrow Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.21.1.12B": translate("FastenerBOM", "Plain Washers, Regular Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.21.1.12C": translate("FastenerBOM", "Plain Washers, Wide Series, ASME B18.21.1, {diameter}"),
    "ASMEB18.3.1A": translate("FastenerBOM", "Hexagon Socket Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.1G": translate("FastenerBOM", "Hexagon Low Head Socket Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.2": translate("FastenerBOM", "Hexagon Socket Flat Countersunk Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.3A": translate("FastenerBOM", "Hexagon Socket Button Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.3B": translate("FastenerBOM", "Hexagon Socket Flanged Button Head Cap Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.4": translate("FastenerBOM", "Hexagon Socket Head Shoulder Screws, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5A": translate("FastenerBOM", "Hexagon Socket Set Screws, Flat Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5B": translate("FastenerBOM", "Hexagon Socket Set Screws, Cone Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5C": translate("FastenerBOM", "Hexagon Socket Set Screws, Dog Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.3.5D": translate("FastenerBOM", "Hexagon Socket Set Screws, Cup Point, ASME B18.3, {diameter} x {length}"),
    "ASMEB18.5.2": translate("FastenerBOM", "Round Head Square Neck Bolts,  ASME B18.5, {diameter} x {length}"),
    "ASMEB18.6.1.2": translate("FastenerBOM", "Slotted Flat Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.3": translate("FastenerBOM", "Type 1 Cross Recessed Flat Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.4": translate("FastenerBOM", "Slotted Oval Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.1.5": translate("FastenerBOM", "Type 1 Cross Recessed Oval Countersunk Head Wood Screws,  ASME B18.6.1, {diameter} x {length}"),
    "ASMEB18.6.3.10A": translate("FastenerBOM", "Slotted Fillister Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.1A": translate("FastenerBOM", "Slotted Flat Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.10B": translate("FastenerBOM", "Type 1 Cross Recessed Fillister Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.1B": translate("FastenerBOM", "Type 1 Cross Recessed Flat Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.12A": translate("FastenerBOM", "Slotted Truss Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.12C": translate("FastenerBOM", "Type 1 Cross Recessed Truss Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.16A": translate("FastenerBOM", "Slotted Round Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.16B": translate("FastenerBOM", "Type 1 Cross Recessed Round Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.4A": translate("FastenerBOM", "Slotted Oval Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.4B": translate("FastenerBOM", "Type 1 Cross Recessed Oval Countersunk Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.9A": translate("FastenerBOM", "Slotted Pan Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.3.9B": translate("FastenerBOM", "Type 1 Cross Recessed Pan Head Machine Screws,  ASME B18.6.3, {diameter} x {length}"),
    "ASMEB18.6.9A": translate("FastenerBOM", "ASME B18.6.9, {diameter} Type A Wing Nut"),
    "DIN84": translate("FastenerBOM", "Cheese head screw DIN 84 - {diameter} x {length}"),
    "DIN96": translate("FastenerBOM", "Wood screw DIN 96 - {diameter} x {length}"),
    "DIN315": translate("FastenerBOM", "Wing nut DIN 315 - {diameter}"),
    "DIN464": translate("FastenerBOM", "Knurled screw DIN 464 - {diameter} x {length}"), # " - St" for material
    "DIN465": translate("FastenerBOM", "Knurled screw DIN 465 - {diameter} x {length}"), # " - St" for material
    "DIN653": translate("FastenerBOM", "Knurled screw DIN 653 - {diameter} x {length}"), # " - St" for material
    "DIN471": translate("FastenerBOM", "Retaining ring DIN 471 - {diameter}"),
    "DIN472": translate("FastenerBOM", "Retaining ring DIN 472 - {diameter}"),
    "DIN478": translate("FastenerBOM", "Square head bolt DIN 478 - {diameter} x {length}"),
    "DIN508": translate("FastenerBOM", "T-Slot Nut DIN 508 - {diameter}"),
    "DIN557": translate("FastenerBOM", "Square nut DIN 557 - {diameter}"),
    "DIN562": translate("FastenerBOM", "Square nut DIN 562 - {diameter}"),
    "DIN571": translate("FastenerBOM", "Wood screw DIN 571 - {diameter} x {length}"),
    "DIN603": translate("FastenerBOM", "Mushroom head square neck bolt  DIN 603 - {diameter} x {length}"),
    "DIN917": translate("FastenerBOM", "Cap nut DIN 917 - {diameter}"),
    "DIN928": translate("FastenerBOM", "Square weld nut DIN 928 - {diameter}"),
    "DIN929": translate("FastenerBOM", "Hexagon weld nut DIN 929 - {diameter}"),
    "DIN933": translate("FastenerBOM", "Hexagon head screw DIN 933 - {diameter} x {length}"),
    "DIN934": translate("FastenerBOM", "Hexagon nut DIN 934 - {diameter}"),
    "DIN935": translate("FastenerBOM", "Hexagon castle nut DIN 935 - {diameter}"),
    "DIN961": translate("FastenerBOM", "Hexagon head screw DIN 961 - {diameter} x {length}"),
    "DIN967": translate("FastenerBOM", "Pan head screw DIN 967 - {diameter} x {length} - H"),
    "DIN985": translate("FastenerBOM", "Prevailing torque type hexagon thin nut DIN 985 - {diameter}"),
    "DIN1143": translate("FastenerBOM", "Nail DIN 1143 - {diameter} - L"), # diameter already includes length -   TODO: include materials on designation
    "DIN1144-A": translate("FastenerBOM", "Nail A {diameter} DIN 1144"), # " - zn" for material
    "DIN1151-A": translate("FastenerBOM", "Nail A {diameter} DIN 1151"), # " - bk" for material
    "DIN1151-B": translate("FastenerBOM", "Nail B {diameter} DIN 1151"), # " - bk"
    "DIN1152": translate("FastenerBOM", "Nail {diameter} DIN 1152"), # " - bk"
    "DIN1160-A": translate("FastenerBOM", "Nail A {diameter} DIN 1160"), # " - bk"
    "DIN1160-B": translate("FastenerBOM", "Nail B {diameter} DIN 1160"), # " - bk"
    "DIN1587": translate("FastenerBOM", "Cap nut - DIN 1587 - {diameter}"),
    "DIN6319C": translate("FastenerBOM", "Spherical washer - DIN 6319 - C - {diameter}"),
    "DIN6319D": translate("FastenerBOM", "Conical seat - DIN 6319 - D - {diameter}"),
    "DIN6319G": translate("FastenerBOM", "Conical seat - DIN 6319 - G - {diameter}"),
    "DIN6330": translate("FastenerBOM", "Hexagon nut DIN 6330 - {diameter}"),
    "DIN6331": translate("FastenerBOM", "Hexagon nut with flange DIN 6331 - {diameter}"),
    "DIN6334": translate("FastenerBOM", "Hexagon nut DIN 6334 - {diameter}"),
    "DIN6340": translate("FastenerBOM", "Washer DIN 6340 - {diameter}"),
    "DIN6799": translate("FastenerBOM", "Retaining ring DIN 6799 - {diameter}"),
    "DIN6912": translate("FastenerBOM", "Hexagon socket head cap screw DIN 6912 - {diameter} x {length}"),
    "DIN7967": translate("FastenerBOM", "Self locking counter nut DIN 7967 - {diameter}"),
    "DIN7984": translate("FastenerBOM", "Hexagon socket head cap screw DIN 7984 - {diameter} x {length}"),
    "DIN7996": translate("FastenerBOM", "Wood screw DIN 7996 - {diameter} x {length}"),
    "EN1661": translate("FastenerBOM", "Hexagon nut with flange EN 1661 - {diameter}"),
    "EN1662": translate("FastenerBOM", "Hexagon head screw with flange EN 1662 - {diameter}"),
    "EN1665": translate("FastenerBOM", "Hexagon head screw with flange EN 1665 - {diameter}"),
    "GN505": translate("FastenerBOM", "T-Slot Nut GN 505 - {diameter} x {slotWidth}"),
    "GN505.4": translate("FastenerBOM", "T-Slot Bolt GN 505.4 - {diameter} x {slotWidth} x {length}"),
    "GN506": translate("FastenerBOM", "T-Slot Nut GN 506 - {diameter} x {slotWidth}"),
    "GN507": translate("FastenerBOM", "T-Slot Nut GN 507 - {diameter} x {slotWidth}"),
    "GOST1144-1": translate("FastenerBOM", "Wood screw GOST 1144-1 - {diameter} x {length}"),
    "GOST1144-2": translate("FastenerBOM", "Wood screw GOST 1144-2 - {diameter} x {length}"),
    "GOST1144-3": translate("FastenerBOM", "Wood screw GOST 1144-3 - {diameter} x {length}"),
    "GOST1144-4": translate("FastenerBOM", "Wood screw GOST 1144-4 - {diameter} x {length}"),
    "GOST11860-1": translate("FastenerBOM", "Cap nut - GOST 11860-1 - {diameter}"),
    "ISO299": translate("FastenerBOM", "T-Slot Nut ISO 299 - {diameter} x {slotWidth}"),
    "ISO1207": translate("FastenerBOM", "Cheese head screw ISO 1207 - {diameter} x {length}"),
    "ISO1234": translate("FastenerBOM", "Split Pin ISO 1234 - {diameter} x {length}"),
    "ISO1580": translate("FastenerBOM", "Pan head screw ISO 1580 - {diameter} x {length}"),
    "ISO2009": translate("FastenerBOM", "Countersunk flat head screw ISO 2009 - {diameter} x {length}"),
    "ISO2010": translate("FastenerBOM", "Countersunk raised head screw ISO 2010 - {diameter} x {length}"),
    "ISO2338": translate("FastenerBOM", "Parallel pin ISO 2338 - {diameter} x {length}"),
    "ISO2339": translate("FastenerBOM", "Taper pin ISO 2339 - {diameter} x {length}"),
    "ISO2340A": translate("FastenerBOM", "Clevis Pin ISO 2340 - A - {diameter} x {length}"),
    "ISO2340B": translate("FastenerBOM", "Clevis Pin ISO 2340 - B - {diameter} x {length}"),
    "ISO2341A": translate("FastenerBOM", "Clevis Pin ISO 2341 - A - {diameter} x {length}"),
    "ISO2341B": translate("FastenerBOM", "Clevis Pin ISO 2341 - B - {diameter} x {length}"),
    "ISO2342": translate("FastenerBOM", "Headless screw ISO 2342 - {diameter} x {length}"),
    "ISO2936": translate("FastenerBOM", "Socket screw key ISO 2936 - {diameter}"),
    "ISO4014": translate("FastenerBOM", "Hexagon head bolt ISO 4014 - {diameter} x {length}"),
    "ISO4015": translate("FastenerBOM", "Hexagon head bolt ISO 4015 - {diameter} x {length}"),
    "ISO4016": translate("FastenerBOM", "Hexagon head bolt ISO 4016 - {diameter} x {length}"),
    "ISO4017": translate("FastenerBOM", "Hexagon head screw ISO 4017 - {diameter} x {length}"),
    "ISO4018": translate("FastenerBOM", "Hexagon head screw ISO 4018 - {diameter} x {length}"),
    "ISO4026": translate("FastenerBOM", "Hexagon socket set screw ISO 4026 - {diameter} x {length}"),
    "ISO4027": translate("FastenerBOM", "Hexagon socket set screw ISO 4027 - {diameter} x {length}"),
    "ISO4028": translate("FastenerBOM", "Hexagon socket set screw ISO 4028 - {diameter} x {length}"),
    "ISO4029": translate("FastenerBOM", "Hexagon socket set screw ISO 4029 - {diameter} x {length}"),
    "ISO4032": translate("FastenerBOM", "Hexagon regular nut ISO 4032 - {diameter}"),
    "ISO4033": translate("FastenerBOM", "Hexagon high nut ISO 4033 - {diameter}"),
    "ISO4034": translate("FastenerBOM", "Hexagon regular nut ISO 4034 - {diameter}"),
    "ISO4035": translate("FastenerBOM", "Hexagon thin nut ISO 4035 - {diameter}"),
    "ISO4161": translate("FastenerBOM", "Hexagon nut with flange ISO 4161 - {diameter}"),
    "ISO4162": translate("FastenerBOM", "Hexagon nut with flange ISO 4162 - {diameter}"),
    "ISO4762": translate("FastenerBOM", "Hexagon socket head cap screw ISO 4762 - {diameter} x {length}"),
    "ISO4766": translate("FastenerBOM", "Set Screw ISO 4766 - {diameter} x {length}"),
    "ISO7040": translate("FastenerBOM", "Prevailing torque type hexagon regular nut ISO 7040 - {diameter}"),
    "ISO7041": translate("FastenerBOM", "Prevailing torque type hexagon nut ISO 7041 - {diameter}"),
    "ISO7043": translate("FastenerBOM", "Prevailing torque type hexagon nut with flange ISO 7043 - {diameter}"),
    "ISO7044": translate("FastenerBOM", "Prevailing torque type hexagon nut with flange ISO 7044 - {diameter}"),
    "ISO7045": translate("FastenerBOM", "Pan head screw ISO 7045 - {diameter} x {length} - H"),
    "ISO7046": translate("FastenerBOM", "Countersunk flat head screw ISO 7046-1 - {diameter} x {length} - H"),
    "ISO7047": translate("FastenerBOM", "Countersunk raised head screw ISO 7047 - {diameter} x {length} - H"),
    "ISO7048": translate("FastenerBOM", "Cheese head screw ISO 7048 - {diameter} x {length} - H"),
    "ISO7049-C": translate("FastenerBOM", "Tapping screw ISO 7049 - {diameter} x {length} - C - H"),
    "ISO7049-F": translate("FastenerBOM", "Tapping screw ISO 7049 - {diameter} x {length} - F - H"),
    "ISO7049-R": translate("FastenerBOM", "Tapping screw ISO 7049 - {diameter} x {length} - R - H"),
    "ISO7089": translate("FastenerBOM", "Washer ISO 7089 - {diameter}"),
    "ISO7090": translate("FastenerBOM", "Washer ISO 7090 - {diameter}"),
    "ISO7092": translate("FastenerBOM", "Washer ISO 7092 - {diameter}"),
    "ISO7093-1": translate("FastenerBOM", "Washer ISO 7093-1 - {diameter}"),
    "ISO7094": translate("FastenerBOM", "Washer ISO 7094 - {diameter}"),
    "ISO7379": translate("FastenerBOM", "Hexagon socket head shoulder screw ISO 7379 - {diameter} x {length}"),
    "ISO7380-1": translate("FastenerBOM", "Hexagon socket button head screw ISO 7380-1 - {diameter} x {length}"),
    "ISO7380-2": translate("FastenerBOM", "Hexagon socket button head screw ISO 7380-2 - {diameter} x {length}"),
    "ISO7434": translate("FastenerBOM", "Set screw ISO 7434 - {diameter} x {length}"),
    "ISO7435": translate("FastenerBOM", "Set screw ISO 7435 - {diameter} x {length}"),
    "ISO7436": translate("FastenerBOM", "Set screw ISO 7436 - {diameter} x {length}"),
    "ISO7719": translate("FastenerBOM", "Prevailing torque type hexagon regular nut ISO 7719 - {diameter}"),
    "ISO7720": translate("FastenerBOM", "Prevailing torque type hexagon nut ISO 7720 - {diameter}"),
    "ISO8673": translate("FastenerBOM", "Hexagon regular nut ISO 8673 - {diameter}"),
    "ISO8674": translate("FastenerBOM", "Hexagon high nut ISO 8674 - {diameter}"),
    "ISO8675": translate("FastenerBOM", "Hexagon thin nut ISO 8675 - {diameter}"),
    "ISO8676": translate("FastenerBOM", "Hexagon head screw ISO 8676 - {diameter} x {length}"),
    "ISO8733": translate("FastenerBOM", "Parallel pin ISO 8733 - {diameter} x {length}"),
    "ISO8734": translate("FastenerBOM", "Parallel pin ISO 8734 - {diameter} x {length}"),
    "ISO8735": translate("FastenerBOM", "Parallel pin ISO 8735 - {diameter} x {length}"),
    "ISO8736": translate("FastenerBOM", "Taper pin ISO 8736 - {diameter} x {length}"),
    "ISO8737": translate("FastenerBOM", "Taper pin ISO 8737 - {diameter} x {length}"),
    "ISO8738": translate("FastenerBOM", "Washer ISO 8738 - {diameter}"),
    "ISO8739": translate("FastenerBOM", "Grooved pin ISO 8739 - {diameter} x {length}"),
    "ISO8740": translate("FastenerBOM", "Grooved pin ISO 8740 - {diameter} x {length}"),
    "ISO8741": translate("FastenerBOM", "Grooved pin ISO 8741 - {diameter} x {length}"),
    "ISO8742": translate("FastenerBOM", "Grooved pin ISO 8742 - {diameter} x {length}"),
    "ISO8743": translate("FastenerBOM", "Grooved pin ISO 8743 - {diameter} x {length}"),
    "ISO8744": translate("FastenerBOM", "Grooved pin ISO 8744 - {diameter} x {length}"),
    "ISO8745": translate("FastenerBOM", "Grooved pin ISO 8745 - {diameter} x {length}"),
    "ISO8746": translate("FastenerBOM", "Grooved pin ISO 8746 - {diameter} x {length}"),
    "ISO8747": translate("FastenerBOM", "Grooved pin ISO 8747 - {diameter} x {length}"),
    "ISO8748": translate("FastenerBOM", "Spring pin ISO 8748 - {diameter} x {length}"),
    "ISO8750": translate("FastenerBOM", "Spring pin ISO 8750 - {diameter} x {length}"),
    "ISO8751": translate("FastenerBOM", "Spring pin ISO 8751 - {diameter} x {length}"),
    "ISO8752": translate("FastenerBOM", "Spring pin ISO 8752 - {diameter} x {length}"),
    "ISO8765": translate("FastenerBOM", "Hexagon head bolt ISO 8765 - {diameter} x {length}"),
    "ISO10511": translate("FastenerBOM", "Prevailing torque type hexagon thin nut ISO 10511 - {diameter}"),
    "ISO10512": translate("FastenerBOM", "Prevailing torque type hexagon regular nut ISO 10512 - {diameter}"),
    "ISO10513": translate("FastenerBOM", "Prevailing torque type hexagon high nut ISO 10513 - {diameter}"),
    "ISO10642": translate("FastenerBOM", "Hexagon socket countersunk head screw ISO 10642 - {diameter} x {length}"),
    "ISO10663": translate("FastenerBOM", "Hexagon nut with flange ISO 10663 - {diameter}"),
    "ISO12125": translate("FastenerBOM", "Prevailing torque type hexagon nut with flange ISO 12125 - {diameter}"),
    "ISO12126": translate("FastenerBOM", "Prevailing torque type hexagon nut with flange ISO 12126 - {diameter}"),
    "ISO13337": translate("FastenerBOM", "Spring pin ISO 13337 - {diameter} x {length}"),
    "ISO14579": translate("FastenerBOM", "Hexalobular socket head cap screw ISO 14579 - {diameter} x {length}"),
    "ISO14580": translate("FastenerBOM", "Hexalobular socket cheese head screw ISO 14580 - {diameter} x {length}"),
    "ISO14582": translate("FastenerBOM", "Countersunk head screw ISO 14582 - {diameter} x {length}"),
    "ISO14583": translate("FastenerBOM", "Hexalobular socket pan head screw ISO 14583 - {diameter} x {length}"),
    "ISO14584": translate("FastenerBOM", "Hexalobular socket raised countersunk head screw ISO 14584 - {diameter} x {length}"),
    "ISO15071": translate("FastenerBOM", "Hexagon bolt with flange ISO 15071 - {diameter}"),
    "ISO15072": translate("FastenerBOM", "Hexagon bolt with flange ISO 15072 - {diameter}"),
    "ISO21670": translate("FastenerBOM", "Weld nut ISO 21670 - {diameter}"),
    "IUTHeatInsert": translate("FastenerBOM", "IUT[A/B/C] Heat staking insert - {diameter}"),
    "NFE27-619": translate("FastenerBOM", "Solid metal finishing washers NFE27-619 - {diameter}"),
    "PCBSpacer": translate("FastenerBOM", "Wurth WA-SSTII PCB Spacer - {diameter} x {length}"),
    "PCBStandoff": translate("FastenerBOM", "Wurth WA-SSTIII PCB Standoff - {diameter} x {length}"),
    "PEMPressNut": translate("FastenerBOM", "PEM self clinching nut - {diameter} x {tcode}"),
    "PEMStandoff": translate("FastenerBOM", "PEM self clinching standoff - {diameter} x {length}"),
    "PEMStud": translate("FastenerBOM", "PEM self clinching stud - {diameter} x {length}"),
    "SAEJ483a1": translate("FastenerBOM", "Low Crown Acorn Hex Nuts, SAEJ483A, {diameter}"),
    "SAEJ483a2": translate("FastenerBOM", "High Crown Acorn Hex Nuts, SAEJ483A, {diameter}"),
    "ThreadedRod": translate("FastenerBOM", "Threaded rod DIN 975 - {diameter} x {length}"),
    "ThreadedRodInch": translate("FastenerBOM", "UNC Threaded Rod, {diameter} x {length}"),
} 
FreeCAD.Console.PrintMessage("fasteners designations length: "+str(len(fastener_designations))+"\n")
# fmt: on


class FSMakeBomCommand:
    """Generate fasteners bill of materials"""

    def GetResources(self):
        icon = os.path.join(iconPath, "IconBOM.svg")
        return {
            "Pixmap": icon,
            "MenuText": translate("FastenerBase", "Generate BOM"),
            "ToolTip": translate("FastenerBase", "Generate fasteners bill of material"),
        }

    def Activated(self):
        bom_items = defaultdict(int)  # starts at zero when a key is not in the dict
        doc = FreeCAD.ActiveDocument
        # setup the header of the spreadsheet
        sheet = doc.addObject("Spreadsheet::Sheet", "Fasteners_BOM")
        sheet.Label = translate("FastenerBOM", "Fasteners_BOM")
        sheet.setColumnWidth("A", 300)
        sheet.set("A1", translate("FastenerBOM", "Type"))
        sheet.set("B1", translate("FastenerBOM", "Qty"))
        sheet.setAlignment("A1:B1", "center|vcenter|vimplied")
        sheet.setStyle("A1:B1", "bold")

        fastener_objects_in_document = [
            x
            for x in doc.Objects
            if hasattr(x, "Proxy") and isinstance(x.Proxy, FSScrewObject)
        ]
        for obj in fastener_objects_in_document:
            # get total count
            fastener_attributes = dict(obj.Proxy.__dict__)  # make a copy
            # format custom lengths nicely
            if hasattr(obj, "lengthCustom") and obj.length == "Custom":
                if obj.Proxy.baseType.startswith(
                    "ASME"
                ) or obj.Proxy.baseType.startswith("SAE"):
                    nice_custom_length = (
                        str(round(obj.lengthCustom.getValueAs("in"), 3)) + "in"
                    )
                else:
                    nice_custom_length = str(
                        round(obj.lengthCustom.getValueAs("mm"), 2)
                    )
                fastener_attributes["length"] = nice_custom_length
            # handle threaded rods
            elif obj.Proxy.baseType == "ThreadedRod":
                if obj.diameter != "Custom":
                    dia_str = obj.diameter
                else:
                    dia_str = "M" + str(round(obj.diameterCustom.getValueAs("mm"), 2))
                len_val = obj.length
                len_str = str(round(len_val.getValueAs("mm"), 2))
                fastener_attributes["length"] = len_str
                fastener_attributes["diameter"] = dia_str
            elif obj.Proxy.baseType == "ThreadedRodInch":
                if obj.diameter != "Custom":
                    dia_str = obj.diameter
                else:
                    dia_str = str(round(obj.diameterCustom.getValueAs("in"), 3)) + "in"
                len_val = obj.length
                len_str = str(round(len_val.getValueAs("in"), 3)) + "in"
                fastener_attributes["length"] = len_str
                fastener_attributes["diameter"] = dia_str

            key = fastener_designations[obj.Proxy.baseType].format(
                **fastener_attributes
            )
            # handle left-handed fasteners:
            if hasattr(obj, "leftHanded") and obj.leftHanded:
                key += " - LH"
            count = GetTotalObjectRepeats(obj)
            bom_items[key] += count

        line = 2
        for fastener in sorted(bom_items.keys()):
            sheet.set(f"A{line}", fastener)
            sheet.set(f"B{line}", str(bom_items[fastener]))
            line += 1
        doc.recompute()
        return

    def IsActive(self):
        return FreeCADGui.ActiveDocument is not None


FreeCADGui.addCommand("Fasteners_BOM", FSMakeBomCommand())
FSCommands.append("Fasteners_BOM", "command")
