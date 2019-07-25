"""
Python implementation of the P(r) inversion
Pinvertor is the base class for the Invertor class
and provides the underlying computations.
"""
import sas.sascalc.pr.py_invertor as py_invertor
#import py_invertor
import numpy as np
import logging
import math
import timeit
from numba import njit

logger = logging.getLogger(__name__)

@njit('u8(f8, f8, f8)')
def accept_q(q, q_min, q_max):
    """
    Check whether a q-value is within acceptable limits.

    :return: 1 if accepted, 0 if rejected.
    """
    if(q_min > 0 and q < q_min):
        return 0
    if(q_max > 0 and q > q_max):
        return 0
    return 1

@njit('b1(f8[:])')
def check_for_zero(x):
    for i in range(len(x)):
        if(x[i] == 0):
            return True
    return False


class Pinvertor:
    #q data
    x = np.empty(0, dtype = np.float)
    #I(q) data
    y = np.empty(0, dtype = np.float)
    #dI(q) data
    err = np.empty(0, dtype = np.float)
    #Number of q points
    npoints = 0
    #Number of I(q) points
    ny = 0
    #Number of dI(q) points
    nerr = 0
    #Alpha value
    alpha = 0.0
    #Slit height in units of q [A-1]
    slit_height = 0.0
    #Slit width in units of q [A-1]
    slit_width = 0.0

    def __init__(self):
        #Maximum distance between any two points in the system
        self.set_dmax(180)
        #Minimum q to include in inversion
        self.set_qmin(-1.0)
        #Maximum q to include in inversion
        self.set_qmax(-1.0)
        #Flag for whether or not to evaluate a constant background
        #while inverting
        self.set_est_bck(0)

    def residuals(self, pars):
        """
        Function to call to evaluate the residuals for P(r) inversion.

        :param pars: input parameters.
        :return: residuals - list of residuals.
        """
        pars = np.float64(pars)

        residuals = []
        residual = 0.0
        diff = 0.0
        regterm = 0.0
        nslice = 25
        regterm = py_invertor.reg_term(pars, self.d_max, nslice)

        for i in range(self.npoints):
            diff = self.y[i] - py_invertor.iq(pars, self.d_max, self.x[i])
            residual = (diff*diff) / (self.err[i]*self.err[i])
            residual += self.alpha * regterm

            try:
                residuals.append(float(residual))
            except:
                raise RuntimeError("Pinvertor.residuals: error setting residual.")

        return residuals

    def pr_residuals(self, pars):
        """
        Function to call to evaluate the residuals for P(r) minimization (for testing purposes).

        :param pars: input parameters.
        :return: residuals - list of residuals.
        """
        pars = np.float64(pars)

        residuals = []
        regterm = 0.0
        nslice = 25
        regterm = py_invertor.reg_term(pars, self.d_max, nslice)

        for i in range(self.npoints):
            diff = self.y[i] - py_invertor.pr(pars, self.d_max, self.x[i])
            residual = (diff*diff) / (self.err[i]*self.err[i])
            residual += self.alpha * regterm
            residuals.append(float(residual))

        return residuals

    def set_x(self, data):
        """
        Function to set the x data.

        :param data: Array of doubles to set x to.
        :return: npoints - Number of entries found, the size of x.
        """
        data = np.float64(data)
        ndata = len(data)

        self.__dict__['x'] = np.zeros(ndata)

        for i in range(ndata):
            self.__dict__['x'][i] = data[i]

        self.__dict__['npoints'] = int(ndata)
        return self.npoints

    def get_x(self, data):
        """
        Function to get the x data.

        :param data: Array to place x into
        :return: npoints - Number of entries found.
        """
        ndata = len(data)
        if (ndata < self.npoints):
            logger.error("Pinvertor.get_x: input array too short for data.")
            return None

        for i in range(self.npoints):
            data[i] = self.x[i]

        return self.npoints


    def set_y(self, data):
        """
        Function to set the y data.

        :param data: Array of doubles to set y to.
        :return: ny - Number of entries found.
        """
        data = np.float64(data)
        ndata = len(data)
        self.__dict__['y'] = np.zeros(ndata)

        for i in range(ndata):
            self.__dict__['y'][i] = data[i]

        self.__dict__['ny'] = int(ndata)
        return self.ny


    def get_y(self, data):
        """
        Function to get the y data.

        :param data: Array of doubles to place y into.
        :return: npoints - Number of entries found.
        """
        ndata = len(data)
        if (ndata < self.ny):
            logger.error("Pinvertor.get_y: input array too short for data.")
            return None

        for i in range(self.ny):
            data[i] = self.y[i]

        return self.npoints

    def set_err(self, data):
        """
        Function to set the err data.

        :param data: Array of doubles to set err to.
        :return: nerr - Number of entries found.
        """
        data = np.float64(data)
        ndata = len(data)
        self.__dict__['err'] = np.zeros(ndata)

        for i in range(ndata):
            self.__dict__['err'][i] = data[i]

        self.__dict__['nerr'] = int(ndata)
        return self.nerr


    def get_err(self, data):
        """
        Function to get the err data.

        :param data: Array of doubles to place err into.
        :return: npoints - number of entries found
        """
        ndata = len(data)
        if (ndata < self.nerr):
            logger.error("Pinvertor.get_err: input array too short for data.")
            return None

        for i in range(self.nerr):
            data[i] = self.err[i]

        return self.npoints

    def set_dmax(self, d_max):
        """
        Sets the maximum distance.

        :param d_max: float to set d_max to.
        :return: d_max
        """
        _d_max = np.float64(d_max)
        self.__dict__['d_max'] = _d_max

        return self.d_max

    def get_dmax(self):
        """
        Gets the maximum distance.

        :return: d_max.
        """
        return self.d_max

    def set_qmin(self, min_q):
        """
        Sets the minimum q.

        :param min_q: float to set q_min to.
        :return: q_min.
        """
        _min_q = np.float64(min_q)
        self._q_min = _min_q
        return self._q_min

    def get_qmin(self):
        """
        Gets the minimum q.

        :return: q_min.
        """
        return self._q_min

    def set_qmax(self, max_q):
        """
        Sets the maximum q.

        :param max_q: float to set q_max to.
        :return: q_max.
        """
        _max_q = np.float64(max_q)
        self._q_max = _max_q
        return self._q_max

    def get_qmax(self):
        """
        Gets the maximum q.

        :return: q_max.
        """
        return self._q_max

    def set_alpha(self, alpha):
        """
        Sets the alpha parameter.

        :param alpha_: float to set alpha to.
        :return: alpha.
        """
        _alpha = np.float64(alpha)
        self.__dict__['alpha'] = _alpha
        return self.alpha

    def get_alpha(self):
        """
        Gets the alpha parameter.

        :return: alpha.
        """
        return self.alpha

    def set_slit_width(self, slit_width):
        """
        Sets the slit width in units of q [A-1].

        :param slit_width: float to set slit_width to.
        :return: slit_width.
        """
        _slit_width = np.float64(slit_width)
        self.__dict__['slit_width'] = _slit_width
        return self.slit_width

    def get_slit_width(self):
        """
        Gets the slit width.

        :return: slit_width.
        """
        return self.slit_width

    def set_slit_height(self, slit_height):
        """
        Sets the slit height in units of q [A-1].

        :param slit_height: float to set slit-height to.
        :return: slit_height.
        """
        _slit_height = np.float64(slit_height)
        self.__dict__['slit_height'] = _slit_height
        return self.slit_height

    def get_slit_height(self):
        """
        Gets the slit height.

        :return: slit_height.
        """
        return self.slit_height

    def set_est_bck(self, est_bck):
        """
        Sets background flag.

        :param est_bck: int to set est_bck to.
        :return: est_bck.
        """
        _est_bck = int(est_bck)
        self.__dict__['est_bck'] = _est_bck
        return self.est_bck

    def get_est_bck(self):
        """
        Gets background flag.

        :return: est_bck.
        """
        return self.est_bck

    def get_nx(self):
        """
        Gets the number of x points.

        :return: npoints.
        """
        return self.npoints

    def get_ny(self):
        """
        Gets the number of y points.

        :return: ny.
        """
        return self.ny

    def get_nerr(self):
        """
        Gets the number of error points.

        :return: nerr.
        """
        return self.nerr

    def iq(self, pars, q):
        """
        Function to call to evaluate the scattering intensity.

        :param pars: c-parameters
        :param q: q.

        :return: I(q)
        """
        q = np.float64(q)
        pars = np.float64(pars)
        pars = np.atleast_1d(pars)

        iq_val = py_invertor.iq(pars, self.d_max, q)
        return iq_val

    def get_iq_smeared(self, pars, q):
        """
        Function to call to evaluate the scattering intensity.
        The scattering intensity is slit-smeared.

        :param pars: c-parameters
        :param q: q, scalar or vector.

        :return: I(q), either scalar or vector depending on q.
        """
        q = np.atleast_1d(q)
        pars = np.float64(pars)
        q = np.float64(q)

        npts = 21
        iq_val = py_invertor.iq_smeared_qvec_njit(pars, q, np.float(self.d_max), self.slit_height,
                                       self.slit_width, npts)
        #If q was a scalar
        if(iq_val.shape[0] == 1):
            return np.asscalar(iq_val)
        return iq_val

    def pr(self, pars, r):
        """
        Function to call to evaluate P(r).

        :param pars: c-parameters.
        :param r: r-value to evaluate P(r) at.

        :return: P(r)
        """
        r = np.float64(r)
        pars = np.float64(pars)
        pars = np.atleast_1d(pars)
        pr_val = py_invertor.pr(pars, self.d_max, r)

        return pr_val

    def get_pr_err(self, pars, pars_err, r):
        """
        Function to call to evaluate P(r) with errors.

        :param pars: c-parameters
        :param pars_err: pars_err.
        :param r: r-value.

        :return: (P(r), dP(r))
        """
        pars = np.atleast_1d(pars)
        pars_err = np.atleast_2d(pars_err)
        pars = np.float64(pars)
        pars_err = np.float64(pars_err)
        r = np.float64(r)

        pr_val = 0.0
        pr_err_val = 0.0
        result = np.zeros(2, dtype = np.float64)

        if(pars_err is None):
            pr_val = np.float64(pr(pars, self.d_max, r))
            pr_err_value = 0.0
            result[0] = pr_val
            result[1] = pr_err_value
        else:
            result = py_invertor.pr_err(pars, pars_err, self.d_max, r)

        return (result[0], result[1])

    def is_valid(self):
        """
        Check the validity of the stored data.

        :return: Returns the number of points if it's all good, -1 otherwise.
        """
        if(self.npoints == self.ny and self.npoints == self.nerr):
            return self.npoints
        else:
            return -1

    def basefunc_ft(self, d_max, n, q):
        """
        Returns the value of the nth Fourier transformed base function.

        :param d_max: d_max.
        :param n: n.
        :param q: q.

        :return: nth Fourier transformed base function, evaluated at q.
        """
        d_max = np.float64(d_max)
        n = int(n)
        q = np.float64(q)
        ortho_val = py_invertor.ortho_transformed(d_max, n, q)

        return ortho_val

    def oscillations(self, pars):
        """
        Returns the value of the oscillation figure of merit for
        the given set of coefficients. For a sphere, the oscillation
        figure of merit is 1.1.

        :param pars: c-parameters.
        :return: oscillation figure of merit.
        """
        nslice = 100
        pars = np.float64(pars)
        pars = np.atleast_1d(pars)

        oscill = py_invertor.reg_term(pars, self.d_max, nslice)
        norm = py_invertor.int_p2(pars, self.d_max, nslice)
        ret_val = np.sqrt(oscill/norm) / np.arccos(-1.0) * self.d_max

        return ret_val

    def get_peaks(self, pars):
        """
        Returns the number of peaks in the output P(r) distribution
        for the given set of coefficients.

        :param pars: c-parameters.
        :return: number of P(r) peaks.
        """
        nslice = 100
        pars = np.float64(pars)
        pars = np.atleast_1d(pars)
        count = py_invertor.npeaks(pars, self.d_max, nslice)

        return count

    def get_positive(self, pars):
        """
        Returns the fraction of P(r) that is positive over
        the full range of r for the given set of coefficients.

        :param pars: c-parameters.
        :return: fraction of P(r) that is positive.
        """
        nslice = 100
        pars = np.float64(pars)
        pars = np.atleast_1d(pars)
        fraction = py_invertor.positive_integral(pars, self.d_max, nslice)

        return fraction

    def get_pos_err(self, pars, pars_err):
        """
        Returns the fraction of P(r) that is 1 standard deviation
        above zero over the full range of r for the given set of coefficients.

        :param pars: c-parameters.
        :param pars_err: pars_err.

        :return: fraction of P(r) that is positive.
        """
        nslice = 51
        pars = np.float64(pars)
        pars_err = np.float64(pars_err)
        fraction = py_invertor.positive_errors(pars, pars_err, self.d_max, nslice)

        return fraction

    def rg(self, pars):
        """
        Returns the value of the radius of gyration Rg.

        :param pars: c-parameters.
        :return: Rg.
        """
        nslice = 101
        pars = np.float64(pars)
        val = py_invertor.rg(pars, self.d_max, nslice)

        return val


    def iq0(self, pars):
        """
        Returns the value of I(q=0).

        :param pars: c-parameters.
        :return: I(q=0)
        """
        nslice = 101
        pars = np.float64(pars)
        val = 4.0 * np.arccos(-1.0) * py_invertor.int_pr(pars, self.d_max, nslice)

        return val



    @staticmethod
    @njit('f8[:,:](f8[:,:], u8, u8, u8, f8, f8, f8, u8, f8[:], f8[:], u8, f8, f8, f8, f8)')
    def _compute_a(a, nfunc, nr, offset, pi, sqrt_alpha, d_max, npoints, x, err, est_bck, slit_height, slit_width, q_min, q_max):
        for j in range(nfunc):
            for i in range(np.uint8(npoints)):
                npts = 21
                if(accept_q(np.float64((x[i])), q_min, q_max) == 1):

                    if(est_bck == 1 and j == 0):
                        a[i, j] = (1.0/err[i])

                    else:
                        if(slit_width > 0 or slit_height > 0):
                            a[i, j] = py_invertor.ortho_transformed_smeared(d_max, j + offset,
                                                                                slit_height, slit_width, x[i], npts)/err[i]
                        else:
                            a[i, j] = py_invertor.ortho_transformed(d_max, j + offset, x[i])/err[i]

            for i_r in range(nr):
                index_i = i_r + npoints
                index_j = j
                if(est_bck == 1 and j == 0):
                    a[index_i, index_j] = 0.0
                else:
                    r = d_max / nr * i_r
                    tmp = np.float64(pi * (j+offset) / d_max)
                    t1 = np.float64(sqrt_alpha * 1.0/nr * d_max * 2.0)
                    t2 = np.float64((2.0 * pi * (j+offset)/d_max * np.cos(pi * (j+offset)*r/d_max)
                    + tmp * tmp * r * np.sin(pi * (j+offset)*r/d_max)))
                    a[index_i, index_j] =  np.float64(t1 * t2)
        return a

    @staticmethod
    @njit('f8[:](f8[:], f8[:], f8[:], f8[:], u8, f8, f8)')
    def _compute_b(b, x, y, err, npoints, q_min, q_max):
        for i in range(npoints):
            if(accept_q(x[i], q_min, q_max)):
                b[i] = np.float64(y[i] / err[i])
        return b

    def _get_matrix(self, nfunc, nr, a_obj, b_obj):
        """
        Returns A matrix and b vector for least square problem.

        :param nfunc: number of base functions.
        :param nr: number of r-points used when evaluating reg term.
        :param a: A array to fill.
        :param b: b vector to fill.

        :return: 0
        """
        nfunc = int(nfunc)
        nr = int(nr)
        a_obj = np.float64(a_obj)
        b_obj = np.float64(b_obj)

        if not (b_obj.shape[0] >= nfunc):
            raise RuntimeError("Pinvertor: b vector too small.")

        if not (a_obj.size >= nfunc*(nr + self.npoints)):
            raise RuntimeError("Pinvertor: a array too small.")

        a = np.float64(a_obj)
        b = np.float64(b_obj)

        sqrt_alpha = np.sqrt(self.alpha)
        pi = np.arccos(-1.0)
        offset = (1, 0)[self.est_bck == 1]

        #Compute zero error case.
        #def check_for_zero(x):
        #    for i, ni in enumerate(x):
        #        if(ni == 0):
        #            return True
        #    return False

        if(check_for_zero(self.err)):
            raise RuntimeError("Pinvertor.get_matrix: Some I(Q) points have no error.")
        #d_max, npoints, x, err, est_bck, slit_height, slit_width):
        a = Pinvertor._compute_a(a, nfunc, nr, offset, pi, sqrt_alpha, self.get_dmax(), self.get_nx(), self.x, self.err, self.est_bck, self.slit_height, self.slit_width, self.get_qmin(), self.get_qmax())
        b = Pinvertor._compute_b(b, self.x, self.y, self.err, self.npoints, self.get_qmin(), self.get_qmax())
        #_compute_b(b, x, y, err, npoints, q_min, q_max)
        return 0


    def _get_invcov_matrix(self, nfunc, nr, a_obj, cov_obj):
        """
        Compute the inverse covariance matrix, defined as inv_cov = a_transposed x a.

        :param nfunc: number of base functions.
        :param nr: number of r-points used when evaluating reg term.
        :param a: A array to fill.
        :param inv_cov: inverse covariance array to be filled.

        :return: 0
        """
        nfunc = int(nfunc)
        nr = int(nr)
        a_obj = np.float64(a_obj)
        cov_obj = np.float64(cov_obj)
        n_a = a_obj.size
        n_cov = cov_obj.size
        a = a_obj
        inv_cov = cov_obj

        if not (n_cov >= (nfunc * nfunc)):
            raise RuntimeError("Pinvertor._get_invcov_matrix: cov array too small.")

        if not (n_a >= (nfunc * (nr + self.npoints))):
            raise RuntimeError("Pinvertor._get_invcov_matrix: a array too small.")

        for i in range(nfunc):
            for j in range(nfunc):
                inv_cov[i, j] = 0.0
                for k in range(nr + self.npoints):
                    inv_cov[i, j] += np.float64(a[k, i]*a[k, j])
        return 0

    def _get_reg_size(self, nfunc, nr, a_obj):
        #in Cinvertor, doc was same as invcov_matrix, left for now -
        """
        Compute the covariance matrix, defined as inv_cov = a_transposed x a.
	    :param nfunc: number of base functions.
	    :param nr: number of r-points used when evaluating reg term.
	    :param a: A array to fill.
	    :param inv_cov: inverse covariance array to be filled.

        :return: 0
        """
        nfunc = int(nfunc)
        nr = int(nfunc)
        a_obj = np.float64(a_obj)
        if not (a_obj.size >= nfunc * (nr + self.npoints)):
            raise RuntimeError("Pinvertor._get_reg_size: input array too short for data.")

        sum_sig = 0.0
        sum_reg = 0.0
        a = a_obj

        for j in range(nfunc):
            for i in range(self.npoints):
                if(accept_q(self.x[i], np.float64(self.get_qmin()), np.float64(self.get_qmax())) == 1):
                    sum_sig += np.float64(a[i, j] * a[i, j])
            for i in range(nr):
                sum_reg += np.float64((a[(i+self.npoints), j]) * (a[(i+self.npoints), j]))

        return sum_sig, sum_reg