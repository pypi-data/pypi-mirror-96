# Vela

This tool is used to compile a
[TensorFlow Lite for Microcontrollers](https://www.tensorflow.org/lite/microcontrollers)
neural network model into an optimised version that can run on an embedded
system containing an
[Arm Ethos-U NPU](https://www.arm.com/products/silicon-ip-cpu).

In order to be accelerated by the Ethos-U NPU the network operators must be
quantised to either 8-bit (unsigned or signed) or 16-bit (signed).

The optimised model will contain TensorFlow Lite Custom operators for those
parts of the model that can be accelerated by the Ethos-U NPU.  Parts of the
model that cannot be accelerated are left unchanged and will instead run on the
Cortex-M series CPU using an appropriate kernel (such as the
[Arm](https://www.arm.com) optimised
[CMSIS-NN](https://github.com/ARM-software/CMSIS_5/tree/develop/CMSIS/NN)
kernels).

After compilation the optimised model can only be run on an Ethos-U NPU
embedded system.

The tool will also generate performance estimates (EXPERIMENTAL) for the
compiled model.

## TensorFlow Support

* Vela 2.1.0 to current supports TensorFlow 2.4
* Vela 2.0.0 to 2.0.1 supports TensorFlow 2.3
* Vela 0.1.0 to 1.2.0 supports TensorFlow 2.1

## Environment

Vela runs on the Linux and Microsoft Windows 10 operating systems, see note in
Installation section below.

## Prerequisites

The following should be installed prior to the installation of Vela:

* Python >= 3.6
* Pip3
* GNU toolchain (GCC, Binutils and libraries)

And optionally:

* Pipenv virtual environment tool

## Installation

Vela is available to install as a package from
[PyPi](https://pypi.org/project/ethos-u-vela/), or as
source code from
[ML Platform](https://review.mlplatform.org/plugins/gitiles/ml/ethos-u/ethos-u-vela).
Both methods will automatically install all the required dependencies.

**Note:** For installing on Microsoft Windows 10 you need to have a C99 capable
toolchain installed.  The recommended and tested toolchain is Microsoft Visual
C++ 14.2 Build Tools, see <https://wiki.python.org/moin/WindowsCompilers>

### PyPi

Install Vela from PyPi using the following command:

```bash
pip3 install ethos-u-vela
```

### ML Platform

First obtain the source code by either downloading the desired TGZ file from:  
<https://review.mlplatform.org/plugins/gitiles/ml/ethos-u/ethos-u-vela>

Or by cloning the git repository:

```bash
git clone https://review.mlplatform.org/ml/ethos-u/ethos-u-vela.git
```

Once you have the source code, Vela can be installed using the following
command:

```bash
pip3 install -U setuptools>=40.1.0
pip3 install .
```

Or, if you use `pipenv`:

```bash
pipenv install .
```

#### Advanced Installation for Developers

If you plan to modify the Vela codebase then it is recommended to install Vela
as an editable package to avoid the need to re-install after every modification.
This is done by adding the `-e` option to the above install commands like so:

```bash
pip3 install -e .
```

Or, if you use `pipenv`:

```bash
pipenv install -e .
```

If you plan to contribute to the Vela project (highly encouraged!) then it is
recommended to install Vela along with the pre-commit tools (see
[Vela Testing](TESTING.md) for more details).

## Running

Vela is run with an input `.tflite` file passed on the command line.  This file
contains the neural network to be compiled.  The tool then outputs an optimised
version with a `_vela.tflite` file prefix, along with the performance estimate
(EXPERIMENTAL) CSV files, all to the output directory.

If you use the `pipenv` virtual environment tool then first start by spawning a
shell in the virtual environment:

```bash
pipenv shell
```

After which running Vela is the same regardless of whether you are in a virtual
environment or not.

Example usage:

1) Compile the network `my_model.tflite`.  The optimised version will be output
to `./output/my_network_vela.tflite`.

```bash
vela my_model.tflite
```

2) Compile the network `/path/to/my_model.tflite` and specify the output to go
in the directory `./results_dir/`.

```bash
vela --output-dir ./results_dir /path/to/my_model.tflite
```

3) Compile a network using a particular Ethos-U NPU.  The following command
selects an Ethos-U65 NPU accelerator configured with 512 MAC units.

```bash
vela --accelerator-config ethos-u65-512 my_model.tflite
```

4) Compile a network using a particular embedded system configuration defined in
Vela's configuration file.  The following command selects the `My_Sys_Config`
system configuration along with the `My_Mem_Mode` memory mode from the `vela_cfg.ini` configuration file.

```bash
vela --config vela_cfg.ini --system-config My_Sys_Config --memory-mode My_Mem_Mode my_model.tflite
```

5) To get a list of all available options (see CLI Options section below):

```bash
vela --help
```

## Example Networks

Some example networks that contain quantised operators which can be compiled by
Vela to run on the Ethos-U NPU can be found at:
<https://tfhub.dev/s?deployment-format=lite&q=quantized>

## APIs

Please see [Vela External APIs](API.md).

## Contributions

Please see [Vela Contributions](CONTRIBUTIONS.md).

## Debug Database

Please see [Vela Debug Database](DEBUG_DB.md).

## Options

Please see [Vela CLI Options](OPTIONS.md).  This includes a description of the
system configuration file format.

## Releases

Please see [Vela Releases](RELEASES.md).

## Security

Please see [Vela Security](SECURITY.md).

## Supported Operators

Please see [Vela Supported Operators](SUPPORTED_OPS.md) for the list of
operators supported in this release.

## Testing

Please see [Vela Testing](TESTING.md).

## Resources

Additional useful information:

* [Arm Products: Ethos-U55 NPU](https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u55)
* [Arm Products: Ethos-U65 NPU](https://www.arm.com/products/silicon-ip-cpu/ethos/ethos-u65)
* [Arm Developer: Ethos-U55 NPU](https://developer.arm.com/ip-products/processors/machine-learning/arm-ethos-u/ethos-u55)
* [Arm Developer: Ethos-U65 NPU](https://developer.arm.com/ip-products/processors/machine-learning/arm-ethos-u/ethos-u65)

## License

Vela is licensed under [Apache License 2.0](LICENSE.txt).
