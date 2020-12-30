const bleno = require('bleno');
const debug = require('debug')('fortiusant:sprc');

const CharacteristicUserDescription = '2901';
const SupportedPowerRange = '2AD8';

class SupportedPowerRangeCharacteristic extends  bleno.Characteristic {
  constructor() {
    debug('[SupportedPowerRangeCharacteristic] constructor');
    super({
      uuid: SupportedPowerRange,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Supported Power Range'
        })
      ],
    });
  }

  onReadRequest(offset, callback) {
    debug('[SupportedPowerRangeCharacteristic] onReadRequest');
    let buffer = new Buffer.alloc(6);
    let at = 0;

    let minimumPower = 0;
    buffer.writeInt16LE(minimumPower, at);
    at += 2;

    let maximumPower = 1000;
    buffer.writeInt16LE(maximumPower, at);
    at += 2;

    let minimumIncrement = 1;
    buffer.writeUInt16LE(minimumIncrement, at);
    at += 2;

    callback(this.RESULT_SUCCESS, buffer);
  }
}

module.exports = SupportedPowerRangeCharacteristic;
