Welcome to nxselector's documentation!
=======================================

Authors: Jan Kotanski

NeXus Component Selector
is a GUI configuration tool dedicated to select components
as well as datasources which constitute the XML configuration strings of
Nexus Data Writer via Sardana NeXus Recorder.

| Source code: https://github.com/nexdatas/selector
| Web page:  https://nexdatas.github.io/selector
| NexDaTaS Web page: https://nexdatas.github.io


------------
Installation
------------

Install the dependencies:

|    Sardana, PyTango, sphinx, Taurus, NXSRecSelector

From sources
^^^^^^^^^^^^

Download the latest version of NeXuS Configuration Server from

|    https://github.com/nexdatas/selector

Extract the sources and run

.. code-block:: console

	  $ python setup.py install

Debian packages
^^^^^^^^^^^^^^^

Debian `buster` and `stretch` or Ubuntu  `focal`, `eoan`, `bionic` packages can be found in the HDRI repository.

To install the debian packages, add the PGP repository key

.. code-block:: console

	  $ sudo su
	  $ wget -q -O - http://repos.pni-hdri.de/debian_repo.pub.gpg | apt-key add -

and then download the corresponding source list, e.g.

.. code-block:: console

	  $ cd /etc/apt/sources.list.d
	  $ wget http://repos.pni-hdri.de/buster-pni-hdri.list

Finally,

.. code-block:: console

	  $ apt-get update
	  $ apt-get install python-nxsrecselector nxselector

To instal other NexDaTaS packages

.. code-block:: console

	  $ apt-get install python-nxswriter nxsconfigtool nxstools python-nxsconfigserver nxsconfigserver-db

and

.. code-block:: console

	  $ apt-get install python-sardana-nxsrecorder nxstaurusgui

for NeXus recorder and MacroGUI packages.

From pip
^^^^^^^^

To install it from pip you need also to install pyqt5, e.g.

.. code-block:: console

   $ python3 -m venv myvenv
   $ . myvenv/bin/activate

   $ pip install pyqt5

   $ pip install nxselector

Moreover it is also good to install

.. code-block:: console

   $ pip install pytango
   $ pip install sardana
   $ pip install nxswriter
   $ pip install nxsrecselector
   $ pip install nxsconfigserver
   $ pip install nxstools
   $ pip install pymysqldb


-------------------
Setting environment
-------------------


Setting Saradna
^^^^^^^^^^^^^^^
If sardana is not yet set up run


.. code-block:: console

	  $ Pool

- enter a new instance name
- create the new instance

Then wait a while until Pool is started and in a new terminal run

.. code-block:: console

	  $ MacroServer

- enter a new instance name
- create the new instance
- connect pool

Next, run Astor and change start-up levels: for Pool to 2,
for MacroServer to 3 and restart servers.

Alternatively, terminate Pool and MacroServer in the terminals and run

.. code-block:: console

          $ nxsetup -s Pool -l2

wait until Pool is started and run

.. code-block:: console

          $ nxsetup -s MacroServer -l3


Additionally, one can create dummy devices by running `sar_demo` in

.. code-block:: console

	  $ spock



Setting NeXus Servers
^^^^^^^^^^^^^^^^^^^^^

To set up  NeXus Servers run

.. code-block:: console

	  $ nxsetup -x

or

.. code-block:: console

          $ nxsetup -x NXSDataWriter
          $ nxsetup -x NXSConfigServer
	  $ nxsetup -x NXSRecSelector

for specific servers.

If the `RecoderPath` property of MacroServer is not set one can do it by

.. code-block:: console

	  $ nxsetup -a /usr/lib/python2.7/dist-packages/sardananxsrecorder

where the path should point the `sardananxsrecorder` package.

General overview
================

----------------
Device Selection
----------------

Every measurement requires devices to be selected. The Component Selector (CS) is a graphical user interface serving this purpose. It is launched from a Linux terminal by

.. code-block:: console

   $ nxselector

or from Spock by

.. code-block:: console

   p09/door/haspp09.01 [1]: nxselector

.. _Figure_1.1:

.. figure:: https://github.com/nexdatas/selector/blob/develop/doc/png/detectors_23.png?raw=true

   Figure 1.1: Component Selector: Detectors

Configuration of the each hardware device for the NeXus files is described inside a configution string, i.e. a configuration component. The employed configuration concept is inspired by the following hardware/configuration correspondences:
.. For more details about NeXus configuration components and their data sources see Section 10.7

| *measurement* <=> *file*
| *experimental setup* <=> *NeXus configuration*
| *hardware device* <=> *component*
| *device attribute*, e.g. counter reading, motor position <=> *data source*
|

The `Figure 1.1` displays the Detectors tab of the Component Selector including the available device components. Composite components are the one with multiple data sources. Simple components are distributed in the frames labelled Counters, ADC, MCA, etc. Components are selected by activating the *Sel.* checkbox. If the *Dis.* checkbox is enabled, the output of the device is displayed during the scan for monitoring purposes.

Simple components may be part of composite components. As a consequence, selecting a composite component may implicitly select one or more simple components. This dependency has to be visible for the users. Therefore, simple components being implicitly selected are deactivated and their font colour changes to grey. The user may also move the mouse over a composite component to inspect the contents.

Ideally all devices are contained in components ensuring that they have sensible NeXus paths and meaningful metadata associated with them. In practice this is not always possible. Consider a counter module with 32 channels. Some of them are permanently connected to specific detectors. It is an easy task to create components for these inputs. However, during the course of a beamtime, it may happen that a researcher needs to record some other signal. Depending on the circumstances it may be impossible to create a new component immediately. Still the new signal has to be recorded. In order to handle this situation, dynamical components have been introduced. They are automatically created whenever a selected device is not covered by a component.

In the upper part of the Selector window the user sets Scan File, Scan Directory and if consecutive scans are appended to one file or stored separately. To use NeXus Sardana Recorder the file extension has to be set to *.nxs* , *.nx* , *.h5*, *.ndf*. **Before the scan all the changes has to be confirmed by the Apply button**. Its action updates settings of the active Sardana measurement group and configuration of the Component Selector.

The Others button of Detectors allows for the user to add simple devices into the measurement group. Its attribute values will be stored for each the scan point.

After devices have been selected and applied the state of all tabs is stored into a profile in the NeXuS Configuration Server. The **profile** contains setting informations, i.e. selected components, user data and file settings, required to prepare configuration for the NeXus writer. The profile extends its measurement group so they share the same name. It is possible to create several profiles. A required profile can be loaded to restore a particular device selection. It is done automatically by changing *MntGrp* in the Selector.

Moreover, by pressing the *Save* or *Load* buttons, the user can save to a file or load the current scan profile. This way, the researcher can easily switch from one data acquisition setup to another.


.. _Figure_1.2:

.. figure:: https://github.com/nexdatas/selector/blob/develop/doc/png/descriptions_23.png?raw=true

   Figure 1.2: Component Selector: Descriptions

The Descriptions tab, `Figure 1.2`, displays components containing metadata which are stored only before or after the scan. They are divided into two groups: the *Mandatory* beamline-specific components and the *Optional* discipline-specific components. The *Mandatory* beamline group describes the source device and the facility. The *Optional* discipline group contains information about the spatial arrangement of the experimental setup, mainly motor positions. The user can select or deselect the optional components from the current profile.

Moreover, the *Reset Desc.* button of Descriptions sets a group of descriptive components to the default one, i.e. defined in the DefaultAutomaticComponents property of the current NXSRecSelector server.

The *Others* button of Descriptions allows for the user to add simple devices into the profile descriptions, i.e. *Other Optional*. Its attribute values will be stored before the scan point.

During appling the selected profile informations from Descriptive components are also stored in the *PreScanSnapshot* door environment variable.
This helps to store the metadata informations by other Sardana recorders.

.. _Figure_1.3:

.. figure:: https://github.com/nexdatas/selector/blob/develop/doc/png/udata_23.png?raw=true

   Figure 1.3: Component Selector: NeXus User Data

In order to describe the experiment completely some of the client data have to be provided by the user. The `Figure 1.3` shows the CS tab allowing the researcher to supply this information. Typical examples for user-supplied metadata are title, sample name and user comment.

The layout of the Component Selector can be easily adapted into different beamline specification in the Configuration tab.

.. The Section 10.8.5 contains more detail description of the settings, i.e. the Configuration tag.

-----
Icons
-----

Icons fetched from http://findicons.com/pack/990/vistaico_toolbar.
