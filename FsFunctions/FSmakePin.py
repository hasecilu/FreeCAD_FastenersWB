# -*- coding: utf-8 -*-
"""
***************************************************************************
*   Copyright (c) 2023                                                    *
*   Original code by:                                                     *
*   hasecilu <hasecilu[at]tuta.io>                                        *
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
import math
import FastenerBase
from screw_maker import FsData

def makePin(self, fa):
    """
    Make a pin, there are different types
    Supported types:
    - Plain taper pins
    - Plain dowel pins
    """

    # TODO: Types of pins
    # Non-exhaustive list of implemented types of pins
    # Video-reference: https://youtu.be/W-0ZV9zXpc0
    # [ ] Clevis pins
    # [ ] Taper pins
    # [X]   Plain taper pins
    # [ ]   Threaded taper pins
    # [ ] Dowel pins
    # [X]   Plain dowel pins
    # [ ]   Tapped dowel pins
    # [ ]   Stepped dowel pins
    # [ ] Roll pins
    # [ ] Grooved pins
    # [ ] Knurled pins
    # [ ] Cotter pins

    if fa.baseType == "ISO2338":
        return makeDowelPin(self, fa)
    if fa.baseType == "ISO2339":
        return makeTaperPin(self, fa)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

def makeDowelPin(self, fa):
    """
    Make a dowel pin
    Supported types:
    - ISO2338: Parallel pins, of unhardened steel and austenitic stainless steel
    """
    l = fa.calc_len
    dia = float(fa.calc_diam.strip(" mm"))
    c, = FsData["ISO2338def"][fa.calc_diam]

    return makeCylindricBody(self, l, dia, c, 15)

def makeTaperPin(self, fa):
    """
    Make a taper pin
    Supported types:
    - ISO2339: Taper pins, unhardened
    """
    l = fa.calc_len
    dia = float(fa.calc_diam.strip(" mm"))
    a, = FsData["ISO2339def"][fa.calc_diam]
    taper = 1/50 # 1:50, m=2%
    D = dia * (1 + taper)

    fm = FastenerBase.FSFaceMaker()
    # NOTE: To simulate a circumference with a BSpline
    # make the first x,y point to be the "corner" that
    # doesn't touch the BSpline and the second point
    # the point of arrival.
    fm.AddPoint(0, 0)
    fm.AddBSpline(dia / 2, 0, dia / 2, -a)
    fm.AddPoint(D / 2, -l + a)
    fm.AddBSpline(D / 2, -l, 0, -l)

    return self.RevolveZ(fm.GetFace())

def makeCylindricBody(self, l, dia, c, alfa):
    """ Creates a basic chamfered rect cylinder """
    fm = FastenerBase.FSFaceMaker()
    fm.AddPoint(0, 0)
    fm.AddPoint(dia / 2 - c * math.sin(math.radians(alfa)), 0)
    fm.AddPoint(dia / 2, -c)
    fm.AddPoint(dia / 2, -l + c)
    fm.AddPoint(dia / 2 - c * math.sin(math.radians(alfa)), -l)
    fm.AddPoint(0, -l)

    return self.RevolveZ(fm.GetFace())

