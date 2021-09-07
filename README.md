# CarbonMeter
Monitor electricity meter to record electricity consumption and calculate associated CO2 produced (CO2 data for UK only), using Raspberry Pi and Espruino microcontroller, with results displayed using Flask web app (optional).

# Background
For this project I was interested in quantifying the amount of CO2 that is produced as a result of my electricity consumption, with an aim to help minimise my environmental impact in this area. This presented a couple of challenges. Firstly, I do not have a smart meter, so don't have easy access to my electricity consumption data (and if I did I suspect I would not be able to get a real-time data feed). Secondly, the amount of CO2 produced by the grid at any one time can change due to variations in demand and weather leading to changes in the mix of renewable and non-renewable energy sources supplying the grid with electricity. I had never worked with microcontrollers or a Raspberry Pi before so this seemed like a great opportunity to experiment with them.

TODO - add picture of carbon intensity graph

I will note that I have since switched to paying for renewable energy and if you do too you may think that this project isn't relevant to you. However, when you are paying for renewable electricity this isn't directed through the grid straight to your home for you to use. You are simply paying for the energy company to replace the amount electricity you use with an equivalent amount of electricity produced by renewables (and not necessarily at the same time that you are using it). This means that the electricity you use at any one time is a mixture of electricity produced by the power stations that are online at that time. So by using electricity and increasing demand at a peak time (e.g. 17:00-20:00 on a week day) when more non-renewable energy sources are being used to meet demand, the electricity you use will have a higher carbon footprint than if you were using it in a period of low demand or in a period of favourable weather conditions for renewables. For this reason it can still be relevant monitoring your electricity and the carbon intensity of the grid in order to minimise your impact (though I'm no expert).

# Overview
This project uses a Raspberry Pi and Espruino microcontroller to record electricity consumption using an existing electricity meter. Most electricity meters have a red LED on the front that will flash when a certain amount of electricity has been used, so by counting the flashes you get the amount of electricty consumed and by recording the time between the flashes you can calculate the rate of consumption. 

To monitor the LED flashes, this project uses a Puck.js Espruino microcontroller with a light dependent resistor (LDR) attached. This was inspired by a [YouTube tutorial](https://www.youtube.com/watch?v=_SsZ3zILFn8&ab_channel=Espruino 'Espruino tutorial') produced by the Espruino YouTube channel. The Puck.js then advertises the LED count and rate over Bluetooth Low Energy (BLE) with an accompanying timestamp, rounded down to whole minutes, which is picked up by the Raspberry Pi and recorded in an SQLite database with a row for each minute. 

TODO - add photo of puck & raspberry pi

For the carbon intensity data, the [Carbon Intensity API](https://carbonintensity.org.uk/ 'Carbon Intennsity API website') provided by National Grid ESO is used. This API is able to provide current and historical carbon intensities and generation mixes for the UK electrical grid, as well as being able to forecast future carbon intesity values. This project uses the historical regional carbon intensity values provided by the API, which provides a more granular carbon intensity based on postcode. At time of writing this feature is currently in beta so only includes the historical forecasted values, as opposed to the actual values; forecasted and actual values were comparable for the whole grid so any differences on a regional level were expected to be acceptable for the purpose of this project. The API is queried every 15 minutes to update the data with carbon intesnity values.

TODO - add carbon intensity graph









