# MLX90641 driver for device tree on a SBC.

**This is a work-in-progess!**

This package provide the I2C routines for the required package `mlx90641-driver-py`.
It uses the I2C from the device tree of a single board computer(SBC).  

- rasberry pi
- jetson nano (NVidia)
- beagle bone


Milestones:
- [x] Raspberry pi + devicetree (`/dev/i2c-<x>`)
- [x] Jetson Nano + devicetree (`/dev/i2c-<x>`)
- [ ] BeagleBone + devicetree (`/dev/i2c-<x>`)


## Dependencies

Driver:
- Python3

## Getting started

### Installation


```bash
pip install mlx90641-driver-devicetree
```

https://pypi.org/project/mlx90641-driver-devicetree  
https://pypistats.org/packages/mlx90641-driver-devicetree

### Running the driver demo

* Connect the EVB to your PC.  
* pen a terminal and run following command:  

```bash
mlx90641-dump-devicetree /dev/i2c-1
```

This program takes 1 optional argument.

```bash
mlx90641-dump-devicetree <communication-port>
```

Note: this dump command is not yet available!
