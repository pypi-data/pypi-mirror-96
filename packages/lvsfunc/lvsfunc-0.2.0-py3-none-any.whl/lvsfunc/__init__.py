"""
    lvsfunc, a collection of VapourSynth functions and wrappers written and/or modified by LightArrowsEXE.

    If you spot any issues, please do not hesitate to send in a Pull Request
    or reach out to me on Discord (LightArrowsEXE#0476)!
"""

# flake8: noqa

from . import aa, comparison, deinterlace, mask, misc, recon, scale

# Aliases:
comp = comparison.compare
diff = comparison.diff
ef = misc.edgefixer
rfs = misc.replace_ranges
scomp = comparison.stack_compare
sraa = aa.upscaled_sraa
src = misc.source
demangle = recon.ChromaReconstruct
crecon = recon.ChromaReconstruct
