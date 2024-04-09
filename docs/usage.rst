.. index:: usage

Usage
=====

EVK with USB interface
----------------------

The most elaborate example is given in ``example/stream_usb.py``.

Navigate to the ``example`` directory and execute:

.. code:: bash

   python3 stream_usb.py

Several options are supported. For an up to date list add ``-h`` to the
above command.

.. note::
   Press 'q' or 'ESC' to quit from the video stream window.
   ``CTRL-C`` also works from the terminal window.
   Closing the video stream widnow will not do however, since this
   window is controled by OpenCV.

For a single image (without the need to have OpenCV, but matplotlib
only):

.. code:: bash

   python3 single_capture_usb.py

Core board or Raspberry Pi uHat
-------------------------------

In this case you work directly with SPI/I2C interfaces. Additionally
you may have `nRESET` and `DATA_READY` pins connected to the host
system. The example shows how to poll the latter, and initiate
thermogram read once it goes high.

Before running the exmaples, make sure the at least ``DATA_READY`` is
connected on you ststem. 
For the uHAT on a Raspberry Pi (3B+ or 4B), the assumptions are:

* MI48 responds to I2C slave address ``0x40``.

To verify that, run on the command prompt:

.. code:: bash

   ls /dev/*i2c*

The response is likely to be:

.. code:: bash

   /dev/i2c-1

Then run (matching the last digit in the above response, ``1`` in this
case):

.. code:: bash

   i2cdetect -y 1

and verify that 40 is listed as a slave.

* MI48's SPI chip select is wired to SPI-0, CE1 (GPIO 07, Header Pin 26) of the Raspberry Pi header

* MI48's ``DATA_READY`` is connected to RPI's header GPIO 24, Header Pin 18



Once the above is cleared, run:

.. code:: bash

   python3 stream_spi.py

For a single image in this mode do:

.. code:: bash

   python3 single_capture_spi.py


.. note::
   The examples are based on the ``SMBus``, ``SpiDev`` and ``gpiozero`` libraries.

   The SMBus and SpiDev librares wrap the corresponding Linux kernel modules
   and provide user space (as opposed to kernel space) access to the I2C and
   SPI drivers. The Python interface exposes a limited subset of the Linux
   functionality however, so some limitations are handled here (e.g. the
   SPI word-width).
   The advantage of using SMbus and SpiDev is that these are generally
   available on linux-running machine, hence the code should be portable to
   boards like RaspberryPI, NVIDIA Jetson, or Xilinx boards running flavours of linux.

   The ``gpiozero`` library is specific to Raspberry Pi and allows pin monitoring
   and control of the J8-header pins on the Raspberry Pi. This allows to monitor
   the ``DATA_READY`` signal of the MI48xx.
   Other boards may have similar libraries.
   The code that is specific to gpiozero is 2 lines, in
   `example/stream_spi.py` only.
