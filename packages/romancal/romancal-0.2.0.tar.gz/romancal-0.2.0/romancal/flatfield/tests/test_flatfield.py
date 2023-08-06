import pytest
import numpy as np

from romancal import datamodels
from romancal.flatfield import FlatFieldStep


@pytest.mark.parametrize(
    "instrument, exptype",
    [
        ("WFI", "WFI_IMAGE"),
    ]
)
@pytest.mark.skip(reason="modifying reference_file_types caused other tests to fail")
def test_flatfield_step_interface(instrument, exptype):
    """Test that the basic inferface works for data requiring a FLAT reffile"""

    shape = (20, 20)

    data = datamodels.ImageModel(shape)
    data.meta.instrument.name = instrument
    data.meta.exposure.type = exptype
    data.meta.subarray.xstart = 1
    data.meta.subarray.ystart = 1
    data.meta.subarray.xsize = shape[1]
    data.meta.subarray.ysize = shape[0]

    flat = datamodels.FlatModel(shape)
    flat.meta.instrument.name = instrument
    flat.meta.subarray.xstart = 1
    flat.meta.subarray.ystart = 1
    flat.meta.subarray.xsize = shape[1]
    flat.meta.subarray.ysize = shape[0]
    flat.data += 1
    flat.data[0,0] = np.nan
    flat.err = np.random.random(shape) * 0.05

    # override class attribute so only the `flat` type needs to be overriden
    # in the step call.
    FlatFieldStep.reference_file_types = ["flat"]
    result = FlatFieldStep.call(data, override_flat=flat)

    assert (result.data == data.data).all()
    assert result.var_flat.shape == shape
    assert result.meta.cal_step.flat_field == 'COMPLETE'
