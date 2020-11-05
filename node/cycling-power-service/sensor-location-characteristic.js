const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:slc');

// https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.sensor_location.xml
let RearHub = 13;

let SensorLocation = '2A65';
let CharacteristicUserDescription = '2901';

class SensorLocationCharacteristic extends  bleno.Characteristic {
  constructor() {
    trace('[SensorLocationCharacteristic] constructor')
    super({
      uuid: SensorLocation,
      value: RearHub,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Sensor Location'
        })
      ],
    });
  }
}

module.exports = SensorLocationCharacteristic;
