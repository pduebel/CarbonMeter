# pi-carbon-energy-meter
Monitor electricity meter to record electricity consumption and calculate associated CO2 produced (CO2 data for UK only), using Raspberry Pi and Espruino microcontroller, with results displayed using Flask web app (optional).

## Background
For this project I was interested in quantifying the amount of CO2 that is produced as a result of my electricity consumption, with an aim to help minimise my environmental impact in this area. This presented a couple of challenges. Firstly, I do not have a smart meter, so don't have easy access to my electricity consumption data (and if I did I suspect I would not be able to get a real-time data feed). Secondly, the amount of CO2 produced by the grid at any one time can change due to variations in demand and weather leading to changes in the mix of renewable and non-renewable energy sources supplying the grid with electricity. I had also never worked with microcontrollers or a Raspberry Pi before, so this seemed like a great opportunity to experiment with them.

I will note that I have since switched to paying for renewable energy and if you do too you may think that this project isn't relevant to you. However, when you are paying for renewable electricity this isn't directed through the grid straight to your home for you to use. You are simply paying for the energy company to replace the amount electricity you use with an equivalent amount of electricity produced by renewables (and not necessarily at the same time that you are using it). This means that the electricity you use at any one time is a mixture of electricity produced by the power stations that are online at that time. So by using electricity and increasing demand at a peak time (e.g. 17:00-20:00 on a week day) when more non-renewable energy sources are being used to meet demand, the electricity you use will have a higher carbon footprint than if you were using it in a period of low demand or in a period of favourable weather conditions for renewables. For this reason it can still be relevant monitoring your electricity and the carbon intensity of the grid in order to minimise your impact (though I'm no expert).

## Overview
This project uses a Raspberry Pi and Espruino microcontroller to record electricity consumption using an existing electricity meter. Most electricity meters have a red LED on the front that will flash when a certain amount of electricity has been used, so by counting the flashes you get the amount of electricty consumed and by recording the time between the flashes you can calculate the rate of consumption. 

To monitor the LED flashes, a Puck.js Espruino microcontroller with a light dependent resistor (LDR) attached is used, inspired by a [YouTube tutorial](https://www.youtube.com/watch?v=_SsZ3zILFn8&ab_channel=Espruino 'Espruino tutorial') produced by the Espruino YouTube channel. The Puck.js then advertises the LED count and rate over Bluetooth Low Energy (BLE) with an accompanying timestamp, rounded down to whole minutes, which is picked up by the Raspberry Pi and recorded in an SQLite database with a row for each minute. 

<img src="https://user-images.githubusercontent.com/56090238/132641577-4b6dca50-3c42-40c6-9b31-3d6502cf4c15.JPG" alt="Puck.js on electricity meter" width="600"/>

<img src="https://user-images.githubusercontent.com/56090238/132641762-198cd278-e809-4ebf-a73f-2d156acaecdf.JPG" alt="Puck.js on electricity meter" width="600"/>


For the carbon intensity data, the [Carbon Intensity API](https://carbonintensity.org.uk/ 'Carbon Intensity API website') provided by National Grid ESO is used. This API is able to provide current and historical carbon intensities and generation mixes for the UK electrical grid, as well as being able to forecast future carbon intesity values. This project uses the historical regional carbon intensity values provided by the API, which provides a more granular carbon intensity based on postcode. At time of writing, this feature is currently in beta so only includes the historical forecasted values, as opposed to the actual values; forecasted and actual values were comparable for the whole grid so any differences on a regional level were expected to be acceptable for the purpose of this project. The API is queried every 15 minutes to update the data with carbon intesnity values.


![image](https://user-images.githubusercontent.com/56090238/132638652-07f9ad1c-bdc3-437a-8aea-e2eb4b4ce5ca.png)


### Optional
The data recorded by the Raspberry Pi is posted to a simple web app for easy viewing, details for setting this up, along with the code needed, can be found in this [repository](https://github.com/pduebel/carbon-meter-website 'Carbon Meter Website'). This is optional and there is a variable in the config file that can be set to False in order to turn off any post requests. The database is posted to the app every 15 minutes, which displays a graph of power consumption and carbon produced over the previous day, week, month, or year, as well as the most recent carbon intensity value. The current power consumption in kW is also displayed, with this value posted by the Raspberry Pi each time it receives an advertisement from the Puck.js. By updating this value more frequently it allows for experimenting with the turning on and off of different devices and appliances to see how much power they consume.


![image](https://user-images.githubusercontent.com/56090238/132638098-e709c3cc-a1c9-462f-b5b8-072d090db91a.png)

## Setup
### Requirements

* Raspberry Pi with BLE and WiFi connectivity (this project used a Zero W)
* Puck.js Espruino microcontroller
* Light dependent resistor (this project used GL5537)
* Soldering equipment (optional - I managed to attach the LDR without soldering)
* Blutack or double-sided tape
* Drill or something similar to make a hole in the case of the Puck.js

### Raspberry Pi

Once you have your Raspberry Pi set up with Raspbian installed, download the files from the github repository using the following commands:
```
sudo apt-get install git
git clone https://github.com/pduebel/pi-carbon-energy-meter.git
```
Then to install the project dependencies, first install `libglib2.0-dev` (required for `bluepy`), then install the packages listed in `requirements.txt`:
```
sudo apt-get install libglib2.0-dev
cd 'pi-carbon-energy-meter/Raspberry Pi'
sudo pip3 install -r requirements.txt
```
Before you're able to run anything, you'll first need to set up your config file. To do this open the `example-config.py` file in the `/Raspberry Pi` directory and set the config variables to the desired values (see section below for getting the MAC address for the Puck.js). Save the new config file as `config.py` in the same directory.

To test that the BLE scanner is working or check that the Puck.js is advertising data, use the `test_ble_scanner.py` script in the `/tests` directory.
Run this from within the `/Raspberry Pi` directory using the command:
```
sudo python3 tests/test_ble_scanner.py
```
This will list all of the devices and associated advertisements detected up by the Raspberry Pi.

Once you have the Puck.js and Raspberry Pi set up and you're ready to run, do so using the following command:
```
sudo python3 receive_puck_ble.py
```
**Note:** The script won't be able to access the Raspberry Pi's BLE unless the it is run using `sudo`.

### Puck.js

This project largely follows the method in the [Espruino DIY Smart Meter Tutorial](https://www.youtube.com/watch?v=_SsZ3zILFn8&ab_channel=Espruino 'Espruino tutorial') (with a modification to the code and without the dashboard) and it's recommended that you use this for a clear, visual guide to setting up the Puck.js.

To summarise, you want to attach the LDR to the D1 and D2 pins either through soldering or bending the wires of the LDR. Then, cut/drill a hole in the plastic back to the Puck.js case to allow the LDR to poke through.

Next, load the `puck-meter.js` file from the `/Puck.js` directory of the repository onto the Puck.js. The easiest way to do this is using the [Espruino Web IDE](https://www.espruino.com/ide/ 'Espruino Web IDE') which requires a computer that has Web Bluetooth available and a compatible browser; make sure to go into the Web IDE settings, `Communications` and check that `Set Current Time` is ticked. Before loading the file you may want to use this opportunity to get the MAC address for the Puck.js which you can do by using the following command in the IDE:
```
NRF.getAddress()
```

For more details and troubleshooting for setting up the Puck.js, read the [quick start guide](https://www.espruino.com/Quick+Start+BLE#puckjs 'Puck.js quick start guide') or [documentation](https://www.espruino.com/Puck.js 'Puck.js documentation') on the Espruino website.

When the Puck.js is all set up, attach it to the front of the electricity meter with the Blutack or double-sided tape with the LDR positioned over the LED.

### Web app (optional)

The code and set up instructions for the optional web app can be found in this [repository](https://github.com/pduebel/carbon-meter-website 'Web app repository').
