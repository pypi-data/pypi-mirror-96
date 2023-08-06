A simple common utils and models package for MRI analysis.

## Functions implemented in MRIUtils

- Train: `from mriutils.train import Train`
- Test: `from mriutils.test import Test`

### Examples

- CUBE-UNet3D for LVMVM dataset: `from mriutils.examples.test_ear3d_lvmvm import Test`

### Datasets

- ACDC: `from mriutils.datasets.acdc import LoadACDC`
- BraTS: `from mriutils.datasets.brats import LoadBraTS`
- MRBrainS: `from mriutils.datasets.mrbrains import LoadMRBrainS`
- H5 files: `from mriutils.datasets.lvmvm import LoadH5`
- MMWHS: `from mriutils.datasets.mmwhs import LoadMMWHS`
- Other `*.png` datasets: `from mriutils.datasets.pngs import LoadPNGS`

### Utils

- Save files:
	- `*.npy`: `from mriutils.utils.tonpy import SaveDataset`
	- `*.nii`/`*.nii.gz`: `from mriutils.utils.tonii import SaveNiiFile`
- Load and save single `*.npy`: `from mriutils.utils.data import Data`
- Load `*.npy` datasets: `from mriutils.utils.load_data import LoadData`
- Normalization: `from mriutils.utils.norm import Normalization`
- Resize: `from mriutils.utils.resize import Resize`
- Show single-layer single-channel images: `from mriutils.utils.show import Show`
- Plot lines: `from mriutils.utils.plots import Plots`
- Timer: `from mriutils.utils.timer import Timer`

### Models

- 2D-UNet: `from mriutils.models.unet import UNet`
- 3D-UNet: `from mriutils.models.unet3d import UNet3D`
- CUBE-UNet3D: `from mriutils.models.cube_unet3d import CUBE_UNet3D`
- Losses: `from mriutils.models.modules.losses import Loss`
- Metrics: `from mriutils.models.modules.metrics import Metric`

### Metrics

- Metrics for MRI Segmentation: `from mriutils.metrics.segmentation import Segmentation`
- Metrics for MRI Synthesis: `from mriutils.metrics.synthesis import Synthesis`

