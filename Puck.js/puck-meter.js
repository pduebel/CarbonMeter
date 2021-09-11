/**
* Code for Puck.js espruino microcontroller.
* 
* Uses LDR to count LED flashes as well as calculating rate of 
* flashes per hour. Then advertises this data, along with battery 
* level, over BLE.
* 
* Contains:
* count // overall count
* rate // rate in flashes per hour
*
* For attaching to front of electricity meter and broadcasting
* data to Raspberry Pi.
*/

var current_time = new Date();
var counter = 0;
var diff = 0;

// Update count & calculate rate
function count() {
  var previous_time = current_time;
  current_time = new Date();
  diff = Math.round(Math.abs(current_time - previous_time)) / 1000;
  rate = Math.round(3600 / diff);
  counter ++;
}
// Update BLE advertising
function update() {
  var a_battery = ArrayBuffer(1);
  var b_battery = new DataView(a_battery);
  b_battery.setUint8(0, E.getBattery(), false);
  var a_counter = ArrayBuffer(4);
  var b_counter = new DataView(a_counter);
  b_counter.setUint32(0, counter, false);
  var a_rate = ArrayBuffer(4);
  var b_rate = new DataView(a_rate);
  b_rate.setUint32(0, rate, false);
  NRF.setAdvertising({},{
    showName:false,
    connectable:true,
    manufacturer:0x0590,
    manufacturerData:[a_battery, a_counter, a_rate],
    interval: 600 // default is 375 - save a bit of power
  });
}

function onInit() {
  clearWatch();
  // Set up pin states
  D1.write(0);
  pinMode(D2,"input_pullup");
  // Watch for pin changes
  setWatch(function(e) {
   count();
   update();
   digitalPulse(LED1,1,1); // show activity
  }, D2, { repeat:true, edge:"falling" });
}