# tilechips
A very simple package to generate tiles for geographic raster data,
build to help user to prepare datasets for deep learning training and
annotation.

tilechips require GDAL to operate.

Please use composite geographic raster (RGB of band combination).

## Requirements
- GDAL
- tqdm

## Installation
### PIP
1. `python -m pip install GDAL`
2. `python -m pip install tilechips`

**or**

### Clone to local directory
1. `git clone https://github.com/wslerry/tilechips.git`
2. `cd tilechips`
3. `python -m pip install GDAL`
4. `python setup.py install`

## Example
```python
from tilechips.tiles import IO

IO(input_image,output_directory,x_size,y_size,save_vrt=False)

```