# MLX90641 driver for EVB90640-41

**This is a work-in-progess!**

This package provide the I2C routines for the required package `mlx90641-driver-py`.
It uses the EVB hardware which connects to the USB host of a computer.

EVB90640-41:
https://www.melexis.com/en/product/EVB90640-41/Evaluation-Board-MLX90640

Milestones:
- [x] win 10 PC + EVB90640-41
- [ ] linux pc + EVB90640-41
- [ ] Raspberry pi + EVB90640-41
- [ ] Jetson Nano + EVB90640-41
- [ ] BeagleBone + EVB90640-41


## Dependencies

Driver:
- Python3
- mlx90641-driver
- pySerial

## Getting started

### Installation


```bash
pip install mlx90641-driver-evb9064x
```

https://pypi.org/project/mlx90641-driver-evb9064x
https://pypistats.org/packages/mlx90641-driver-evb9064x

### Running the driver demo

* Connect the EVB to your PC.  
* pen a terminal and run following command:  

```bash
mlx90641-dump-evb9064x auto
```

This program takes 1 optional argument.

```bash
mlx90641-dump-evb9064x <communication-port>
```

Note: this dump command is not yet available!
