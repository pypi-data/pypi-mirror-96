#  PyTransit: fast and easy exoplanet transit modelling in Python.
#  Copyright (C) 2010-2020  Hannu Parviainen
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from typing import Union

from astropy.constants import R_sun, M_sun
from matplotlib.patches import Circle
from matplotlib.pyplot import subplots, setp
from numpy import linspace, sin, cos, array, ndarray, asarray, squeeze, cross, newaxis, pi, where, nan, full, degrees
from numpy.linalg import norm
from scipy.spatial.transform.rotation import Rotation

from .transitmodel import TransitModel
from .numba.osmodel import create_star_xy, create_planet_xy, map_osm, xy_taylor_vt, luminosity_v, oblate_model_s, \
    luminosity_v2
from ..orbits import as_from_rhop, i_from_baew
from ..orbits.taylor_z import vajs_from_paiew, find_contact_point
from ..utils.octasphere import octasphere


class OblateStarModel(TransitModel):
    """Transit model for a gravity-darkened fast-rotating oblate star.

    Transit model for a gravity-darkened fast-rotating oblate star following Barnes (ApJ, 2009, 705).
    """
    def __init__(self, rstar: float = 1.0, wavelength: float = 510, sres: int = 80, pres: int = 5, tres: int = 60):
        """

        Parameters
        ----------
        rstar
            Stellar radius [R_Sun]
        wavelength
            Effective wavelength [nm]
        sres
            Stellar discretization resolution
        pres
            Planet discretization resolution
        """
        super().__init__()

        self.rstar = rstar*R_sun.value     # Stellar equator radius  [m]
        self.wavelength = wavelength*1e-9  # Effective wavelength    [m]
        self.sres = sres                   # Integration resolution for the star
        self.pres = pres                   # Integration resolution for the planet
        self.tres = tres

        self._ts, self._xs, self._ys = create_star_xy(sres)
        self._xp, self._yp = create_planet_xy(pres)

    def visualize(self, k, p, rho, b, e, w, alpha, rperiod, tpole, istar, beta, ldc, figsize=(5, 5), ax=None,
                  ntheta=18):
        if ax is None:
            fig, ax = subplots(figsize=figsize)
            ax.set_aspect(1.)
        else:
            fig, ax = None, ax

        a = as_from_rhop(rho, p)
        inc = i_from_baew(b, a, e, w)
        mstar, ostar, gpole, f, _ = map_osm(rstar=self.rstar, rho=rho, rperiod=rperiod, tpole=tpole, phi=0.0)

        # Plot the star
        # -------------
        vertices_original, faces = octasphere(4)
        vertices = vertices_original.copy()
        vertices[:, 1] *= (1.0 - f)

        triangles = vertices[faces]
        centers = triangles.mean(1)
        normals = cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
        nlength = norm(normals, axis=1)
        normals /= nlength[:, newaxis]

        rotation = Rotation.from_rotvec((0.5 * pi - istar) * array([1, 0, 0]))
        rn = rotation.apply(normals)
        rc = rotation.apply(centers)

        mask = rn[:, 2] < 0.0
        l = luminosity_v2(centers[mask], normals[mask], istar, mstar, self.rstar, ostar, tpole, gpole, beta,
                         ldc, self.wavelength)
        ax.tripcolor(rc[mask, 0], rc[mask, 1], l, shading='gouraud')

        nphi = 180
        theta = linspace(0 + 0.1, pi - 0.1, ntheta)
        phi = linspace(0, 2 * pi, nphi)
        for i in range(theta.size):
            y = (1.0 - f) * cos(theta[i])
            x = cos(phi) * sin(theta[i])
            z = sin(phi) * sin(theta[i])
            v = rotation.apply(array([x, full(nphi, y), z]).T)
            m = v[:, 2] < 0.0
            ax.plot(where(m, v[:, 0], nan), v[:, 1], 'k--', lw=1.5, alpha=0.25)

        # Plot the orbit
        # --------------
        y0, vx, vy, ax_, ay, jx, jy, sx, sy = vajs_from_paiew(p, a, inc, e, w)
        c1 = find_contact_point(k, 1, y0, vx, vy, ax_, ay, jx, jy, sx, sy)
        c4 = find_contact_point(k, 4, y0, vx, vy, ax_, ay, jx, jy, sx, sy)
        time = linspace(2 * c1, 2 * c4, 100)

        ox, oy = xy_taylor_vt(time, alpha, y0, vx, vy, ax_, ay, jx, jy, sx, sy)
        ax.plot(ox, oy, 'k')

        pxy = xy_taylor_vt(array([0.0]), alpha, y0, vx, vy, ax_, ay, jx, jy, sx, sy)
        ax.add_artist(Circle(pxy, k, zorder=10, fc='k'))

        # Plot the info
        # -------------
        ax.text(0.025, 0.95, f"i$_\star$ = {degrees(istar):.1f}$^\circ$", transform=ax.transAxes)
        ax.text(0.025, 0.90, f"i$_\mathrm{{p}}$ = {degrees(inc):.1f}$^\circ$", transform=ax.transAxes)
        ax.text(1 - 0.025, 0.95, fr"$\alpha$ = {degrees(alpha):.1f}$^\circ$", transform=ax.transAxes, ha='right')
        ax.text(0.025, 0.05, f"f = {f:.1f}", transform=ax.transAxes)

        setp(ax, xlim=(-1.1, 1.1), ylim=(-1.1, 1.1), xticks=[], yticks=[])
        if fig is not None:
            fig.tight_layout()
        return ax

    def evaluate_ps(self, k: Union[float, ndarray], rho: float, rperiod: float, tpole: float, phi: float,
                    beta: float, ldc: ndarray, t0: float, p: float, a: float, i: float, l: float = 0.0,
                    e: float = 0.0, w: float = 0.0, copy: bool = True) -> ndarray:
        """Evaluate the transit model for a set of scalar parameters.

        Parameters
        ----------
        k : array-like
            Radius ratio(s) either as a single float or an 1D array
        rho : float
            Stellar density [g/cm^3]
        rperiod : float
            Stellar rotation period [d]
        tpole : float
            Temperature at the pole [K]
        phi : float
            Star's obliquity to the plane of the sky [rad]
        beta: float
            Gravity darkening parameter
        ldc : array-like
            Limb darkening coefficients as a 1D array
        t0 : float
            Zero epoch
        p : float
            Orbital period [d]
        a : float
            Scaled orbital semi-major axis [R_star]
        i : float
            Orbital inclination [rad]
        l : float
            Orbital azimuth angle [rad]
        e : float, optional
            Orbital eccentricity
        w : float, optional
            Argument of periastron

        Notes
        -----
        This version of the `evaluate` method is optimized for calculating a single transit model (such as when using a
        local optimizer). If you want to evaluate the model for a large number of parameters simultaneously, use either
        `evaluate` or `evaluate_pv`.

        Returns
        -------
        ndarray
            Modelled flux as a 1D ndarray.
        """

        ldc = asarray(ldc)
        k = asarray(k)

        if self.time is None:
            raise ValueError("Need to set the data before calling the transit model.")
        if ldc.size != 2*self.npb:
            raise ValueError("The quadratic model needs two limb darkening coefficients per passband")

        mstar, ostar, gpole, f, feff = map_osm(self.rstar, rho, rperiod, tpole, phi)
        sphi, cphi = sin(phi), cos(phi)

        flux = oblate_model_s(self.time, k, t0, p, a, l, i, e, w, ldc, mstar, self.rstar, ostar, tpole, gpole,
                              f, feff, sphi, cphi, beta, self.wavelength, self.tres, self._ts, self._xs, self._ys, self._xp, self._yp,
                              self.lcids, self.pbids, self.nsamples, self.exptimes, self.npb)

        return squeeze(flux)