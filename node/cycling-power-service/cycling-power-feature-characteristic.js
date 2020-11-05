const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:cpfc');

// https://www.bluetooth.com/wp-content/uploads/Sitecore-Media-Library/Gatt/Xml/Characteristics/org.bluetooth.characteristic.cycling_power_feature.xml
let CrankRevolutionDataSupported = 0x08;

let CharacteristicUserDescription = '2901';
let CyclingPowerFeature = '2A65';

class CyclingPowerFeatureCharacteristic extends  bleno.Characteristic {
  constructor() {
    trace('[CyclingPowerFeatureCharacteristic] constructor')
    let flags = new Buffer.alloc(4)
    flags.writeUInt32LE(CrankRevolutionDataSupported)

    super({
      uuid: CyclingPowerFeature,
      value: flags,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Cycling Power Feature'
        })
      ],
    });
  }
}

module.exports = CyclingPowerFeatureCharacteristic;
