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
from FreeCAD import Base
import FastenerBase
from screw_maker import FsData

def makeSelfTappingScrew(self, fa):
    """
    Make a self tapping screw, used on sheet metal and plastic holes
    Supported types:
    - ISO7049-[C/F/R]: Cross-recessed pan head tapping screws
    """
    if fa.baseType[:7] == "ISO7049":
        return makeISO7049(self, fa)

    raise NotImplementedError(f"Unknown fastener type: {fa.baseType}")

def makeISO7049(self, fa):
    """
    Make an ISO7049 Cross-recessed pan head tapping screw
    Variations:
    - ISO7049-C: Self tapping screw with conical point
    - ISO7049-F: Self tapping screw with flat point
    - ISO7049-R: Self tapping screw with round point
    """
    SType = fa.baseType
    l = fa.calc_len
    # Convert from string "ST x.y" to x.y float
    dia = float(fa.calc_diam.split()[1])

    # NOTE: The norm ISO1478 defines: "Tapping screws thread"
    # Read data from the thread norm definition
    # instead of duplicating it on the screw definition.
    P, _, _, d2_max, d2_min, d3_max, d3_min, _, rR, yC, yF, yR, _ = \
        FsData["iso1478def"][fa.calc_diam]
    d2 = getAverage(d2_min, d2_max)
    d3 = getAverage(d3_min, d3_max)

    _, dk_max, dk_min, k_max, k_min, r, _, PH, m, h_max, h_min = fa.dimTable
    D = getAverage(dk_min, dk_max)
    K = getAverage(k_min, k_max)
    h = getAverage(h_min, h_max)

    b = l # length for th thread from the tip
    full_length = True

    ri = d2 / 2.0   # inner thread radius
    ro = dia / 2.0  # outer thread radius

    # inner radius of screw section
    sr = ro
    if fa.thread:
        sr = ri

    # length of cylindrical part where thread begins to grow.
    slope_length = ro - ri

    # FIXME:
    # It seems to be a tbat the y values don't affect or
    # at least are not needed to create the thread.
    # Check if tips are being done properly,
    # if SType == "ISO7049-C":
    #     tip_length = yC
    # if SType == "ISO7049-F":
    #     tip_length = yF
    # if SType == "ISO7049-R":
    #     tip_length = yR
    # FreeCAD.Console.PrintMessage("y : Length of incomplete thread\n")
    # FreeCAD.Console.PrintMessage("yC: "+str(yC) + "\n")
    # FreeCAD.Console.PrintMessage("yF: "+str(yF) + "\n")
    # FreeCAD.Console.PrintMessage("yR: "+str(yR) + "\n")

    ###########################
    # Make full screw profile #
    ###########################

    # calculation of screw tip length
    # Sharpness of screw tip is equal 40 degrees. If imagine half of screw tip
    # as a triangle, then acute-angled angle of the triangle (alpha) be which
    # is equal to half of the screw tip angle.
    alpha = 45/2
    # And the adjacent cathetus be which is equal to least screw radius (sr)
    # Then the opposite cathetus can be getted by formula: tip_length=sr/tg(alpha)
    tip_length = sr/math.tan(math.radians(alpha))
    if SType == "ISO7049-F":
        tip_length = sr - d3 / 2

    # FreeCAD.Console.PrintMessage("tip l at 45°: "+str(tip_length) + "\n")

    fm = FastenerBase.FSFaceMaker()

    # 1) screw head
    # Head of screw builds by B-Spline instead two arcs builded by two radii
    # (values R1 and R2). A curve built with two arcs and a curve built with a
    # B-Spline are almost identical. That can be verified if build a contour of
    # screw head by two ways in Sketch workbench and compare them. B-Spline also
    # allows to remove the contour that appears between two arcs during creation
    # process, and it use fewer points than two arcs.
    fm.AddPoint(0, K)
    fm.AddBSpline(D/2, K, D/2, 0)

    # 2) add rounding under screw head
    rr = r
    fm.AddPoint(ro+rr, 0)      # first point of rounding
    if fa.thread and full_length:
        fm.AddBSpline(ro, 0, sr, -slope_length) # create spline rounding
    else:
        fm.AddArc2(+0, -rr, 90) # in other cases create arc rounding

    # 3) cylindrical part (place where thread will be added)
    if not full_length:
        if fa.thread:
            fm.AddPoint(ro, -l+b+slope_length)    # entery point of thread
        fm.AddPoint(sr, -l+b)   # start of full width thread b >= l*0.6

    # tip shape
    if SType == "ISO7049-C":
        fm.AddPoint(sr, -l+tip_length)
        fm.AddPoint(0, -l)
    if SType == "ISO7049-F":
        fm.AddPoint(sr, -l+tip_length)
        fm.AddPoint(d3 / 2, -l)
        fm.AddPoint(0, -l)
    if SType == "ISO7049-R":
        fm.AddPoint(sr, -l+tip_length)
        angle = 45
        fm.AddPoint(rR*math.cos(math.radians(angle)), rR-l)
        fm.AddArc2(-rR*math.cos(math.radians(angle)),
                   rR*math.sin(math.radians(angle)), -angle)

    # make profile from points (lines and arcs)
    profile = fm.GetFace()

    # make screw solid body by revolve a profile
    screw = self.RevolveZ(profile)

    # make slot in screw head
    recess = self.makeHCrossRecess(PH, m)
    recess = recess.translate(Base.Vector(0.0, 0.0, h))
    screw = screw.cut(recess)

    # make thread
    if fa.thread:
        if SType == "ISO7049-C":
            # vanilla usage
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l, ri, ro, P)
        if SType == "ISO7049-F":
            # sent flag to omit the tip thread
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l, ri, ro, P, True)
        if SType == "ISO7049-R":
            # move the tip a little up to compensate roundness
            thread = self.makeDin7998Thread(-l+b+slope_length, -l+tip_length,
                                            -l+rR, ri, ro, P)
        screw = screw.fuse(thread)

    return screw

def getAverage(lower_limit, upper_limit):
    """ ISO norms give an interval for some dimensions, use average """
    return (lower_limit + upper_limit) / 2
