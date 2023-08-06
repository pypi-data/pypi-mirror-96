#! /usr/bin/env python
#
import logging
import numpy as np

from ..stpipe import Step
from .. import datamodels
from . import ramp_fit

from . import JWST   # 020821 syntax ?
from . import Roman   # 020821 syntax ?

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


__all__ = ["RampFitStep"]


class RampFitStep (Step):

    """
    This step fits a straight line to the value of counts vs. time to
    determine the mean count rate for each pixel.
    """

    spec = """
        opt_name = string(default='')
        maximum_cores = option('none','quarter','half','all',default='none')
            # max number of processes to create
    """

    # Prior to 04/26/17, the following were also in the spec above:
    #      algorithm = option('OLS', 'GLS', default='OLS') # 'OLS' or 'GLS'
    #      weighting = option('unweighted', 'optimal', default='unweighted') \
    #      # 'unweighted' or 'optimal'
    # As of 04/26/17, the only allowed algorithm is 'ols', and the
    #      only allowed weighting is 'optimal'.

    algorithm = 'ols'      # Only algorithm allowed ?
#    algorithm = 'gls'

    weighting = 'optimal'  # Only weighting allowed ?

    reference_file_types = ['readnoise', 'gain']

    def process(self, input):

        # Open input as a Roman DataModel (single integration; 3D arrays)
        with Roman.datamodels.RampModel(input) as R_input_model:  # syntax ?

            # Create a JWST DataModel (4D arrays) to populate
            input_model = JWST.datamodels.RampModel()  # syntax ?

            # Populate JWST model with correct sized arrays from Roman model
            input_model.meta = R_input_model.meta
            input_model.data = np.broadcast_to(R_input_model.data, (1,) +
                                               R_input_model.data.shape)

            input_model.pixeldq = R_input_model.pixeldq

            input_model.groupdq = np.broadcast_to(R_input_model.groupdq, (1,) +
                                                  R_input_model.groupdq.shape)

            input_model.err = np.broadcast_to(R_input_model.err, (1,) +
                                              R_input_model.err.shape)

            input_model.refout = np.broadcast_to(R_input_model.refout, (1,) +
                                                 R_input_model.refout.shape)

            max_cores = self.maximum_cores
            readnoise_filename = self.get_reference_file(input_model,
                                                         'readnoise')
            gain_filename = self.get_reference_file(input_model, 'gain')

            log.info('Using READNOISE reference file: %s', readnoise_filename)
            readnoise_model = datamodels.ReadnoiseModel(readnoise_filename)
            log.info('Using GAIN reference file: %s', gain_filename)
            gain_model = datamodels.GainModel(gain_filename)

            # Try to retrieve the gain factor from the gain reference file.
            # If found, store it in the science model meta data, so that it's
            # available later in the gain_scale step, which avoids having to
            # load the gain ref file again in that step.
            if gain_model.meta.exposure.gain_factor is not None:
                input_model.meta.exposure.gain_factor = \
                    gain_model.meta.exposure.gain_factor

            log.info('Using algorithm = %s' % self.algorithm)
            log.info('Using weighting = %s' % self.weighting)

            buffsize = ramp_fit.BUFSIZE
            if self.algorithm == "GLS":
                buffsize //= 10

            out_model, int_model, opt_model, gls_opt_model = ramp_fit.ramp_fit(
                input_model, buffsize,
                readnoise_model, gain_model, self.algorithm,
                self.weighting, max_cores
            )
            # The above int_model is None

            # Remove the empty 0th dimension from the JWST model and insert
            # the results into the Roman DataModel
            R_input_model.data = input_model.data[-1]
            R_input_model.groupdq = input_model.groupdq[-1]
            R_input_model.err = input_model.err[-1]
            R_input_model.refout = input_model.refout[-1]

            readnoise_model.close()
            gain_model.close()

        # Save the OLS optional fit product, if it exists
        if opt_model is not None:
            self.save_model(opt_model, 'fitopt', output_file=self.opt_name)

        # Save the GLS optional fit product, if it exists
        if gls_opt_model is not None:
            self.save_model(
                gls_opt_model, 'fitoptgls', output_file=self.opt_name
            )

        if out_model is not None:
            out_model.meta.cal_step.ramp_fit = 'COMPLETE'

        return out_model, None  # 'None' for int_model
