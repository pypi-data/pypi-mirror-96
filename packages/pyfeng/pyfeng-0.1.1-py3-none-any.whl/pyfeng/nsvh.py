import numpy as np
import scipy.stats as spst
#import numpy.polynomial as nppoly
from. import sabr


class Nsvh1(sabr.SabrABC):
    """
    Hyperbolic Normal Stochastic Volatility (NSVh) model with lambda=1 by Choi et al. (2019)

    References:
        Choi, J., Liu, C., & Seo, B. K. (2019). Hyperbolic normal stochastic volatility model.
        Journal of Futures Markets, 39(2), 186–204. https://doi.org/10.1002/fut.21967
    """

    beta = 0.0  # beta is already defined in the parent class, but the default value set as 0

    def __init__(self, sigma, vov=0.0, rho=0.0, intr=0.0, divr=0.0, is_fwd=False):
        """
        Args:
            sigma: model volatility at t=0
            vov: volatility of volatility
            rho: correlation between price and volatility
            intr: interest rate (domestic interest rate)
            divr: dividend/convenience yield (foreign interest rate)
            is_fwd: if True, treat `spot` as forward price. False by default.
        """
        # Make sure beta = 0
        super().__init__(sigma, vov, rho, beta=0, intr=intr, divr=divr, is_fwd=is_fwd)

    def price(self, strike, spot, texp, cp=1):
        disc_fac = np.exp(-texp * self.intr)
        fwd = spot * (1.0 if self.is_fwd else np.exp(-texp * self.divr)/disc_fac)

        s_sqrt = self.vov * np.sqrt(texp)
        sig_sqrt = self.sigma * np.sqrt(texp)
        vov_var = np.exp(0.5 * s_sqrt**2)
        rhoc = np.sqrt(1 - self.rho**2)

        d = (np.arctanh(self.rho) + np.arcsinh(((fwd-strike)*s_sqrt/sig_sqrt - self.rho*vov_var)/rhoc)) / s_sqrt
        ncdf_p = spst.norm.cdf(cp*(d + s_sqrt))
        ncdf_m = spst.norm.cdf(cp*(d - s_sqrt))
        ncdf = spst.norm.cdf(cp*d)

        price = 0.5*sig_sqrt/s_sqrt*vov_var\
            * ((1+self.rho)*ncdf_p - (1-self.rho)*ncdf_m - 2*self.rho*ncdf)\
            + (fwd-strike) * ncdf
        price *= cp * disc_fac
        return price

    def cdf(self, strike, spot, texp, cp=-1):
        """
        Cumulative distribution function under NSVh (lambda=1) distribution.

        Args:
            strike: strike price
            spot: spot (or forward)
            texp:
            cp: -1 for left-tail (CDF), -1 for right-tail (survival function)

        Returns:
            CDF value
        """
        fwd = spot * (1.0 if self.is_fwd else np.exp((self.intr - self.divr)*texp))

        s_sqrt = self.vov * np.sqrt(texp)
        sig_sqrt = self.sigma * np.sqrt(texp)
        vov_var = np.exp(0.5 * s_sqrt**2)
        rhoc = np.sqrt(1 - self.rho**2)

        d = (np.arctanh(self.rho) +
             np.arcsinh(((fwd - strike) * s_sqrt / sig_sqrt - self.rho * vov_var) / rhoc)) / s_sqrt
        return spst.norm.cdf(cp*d)
