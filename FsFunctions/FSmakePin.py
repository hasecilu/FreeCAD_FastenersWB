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
import FreeCAD
import Part
import FastenerBase
from screw_maker import FsData, sqrt2

def makePin(self, fa):
    """
    Make a pin, there are different types
    Supported types:
    - Single hole clevis pins without head
    - Single hole clevis pins with head
    - Plain taper pins
    - Plain dowel pins
    """

    # TODO: Implement more types of pins
    # GitHub issue: https://github.com/shaise/FreeCAD_FastenersWB/issues/318

    if fa.baseType == "ISO2338":
        return makeDowelPin(self, fa)
    if fa.baseType == "ISO2339":
        return makeTaperPin(self, fa)
    if fa.baseType == "ISO2340":
        return makeClevisPinWithoutHead(self, fa)
    if fa.baseType[:7] == "ISO2341":
        return makeClevisPinWithHead(self, fa)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

def makeClevisPinWithoutHead(self, fa):
    """
    Make a clevis pin
    Supported types:
    - ISO2340: Clevis pins without head
    """
    l = fa.calc_len
    dia = float(fa.calc_diam.strip(" mm"))
    dl, c, le = FsData["ISO2340def"][fa.calc_diam]

    clevis = makeCylindricBody(self, l, dia, c, 30)
    clevis = makeTraversalHoles(clevis, dl, dia, [-le, -l+le])
    return clevis

def makeClevisPinWithHead(self, fa):
    """
    Make a clevis pin
    Supported types:
    - ISO2341-A: Clevis pins with head, without split pin hole
    - ISO2341-B: Clevis pins with head, with split pin hole
    """
    l = fa.calc_len
    dia = float(fa.calc_diam.strip(" mm"))
    # ISO2341-A and ISO2341-B have same data
    dk, dl, c, e, k, le, r = FsData["ISO2341-Adef"][fa.calc_diam]

    fm = FastenerBase.FSFaceMaker()
    # head
    fm.AddPoint(0, k)
    fm.AddPoint(dk / 2 - e / sqrt2, k) # cos(45)=1/sqrt(2)
    fm.AddPoint(dk / 2, k-e)
    fm.AddPoint(dk / 2, 0)
    # rounding under head
    fm.AddPoint(dia / 2 + r, 0)
    fm.AddBSpline(dia / 2, 0, dia / 2, -r)
    # shaft
    fm.AddPoint(dia / 2, -l + c)
    fm.AddPoint(dia / 2 - c / 2, -l) # sin(30)=1/2
    fm.AddPoint(0, -l)

    clevis = self.RevolveZ(fm.GetFace())
    if fa.baseType == "ISO2341-B":
        clevis = makeTraversalHoles(clevis, dl, dia, [-l+le])

    return clevis

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

def makeTraversalHoles(self, d, h, les):
    """ Create passing holes on z distances in 'les' array """
    for le in les:
        hole = Part.makeCylinder(d / 2, h)
        hole.Placement = FreeCAD.Placement(
            FreeCAD.Vector(0, h / 2, le), FreeCAD.Rotation(FreeCAD.Vector(1, 0, 0), 90)
        )
        self = self.cut(hole)

    return self
