
const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:uc4');

const CharacteristicUserDescription = '2901';
const UnknownFeature4 = '347b0019-7635-408b-8918-8ff3949ce592';

class UnknownCharacteristic4 extends bleno.Characteristic {
  constructor() {
    trace('[UnknownCharacteristic4] constructor');
    super({
      uuid: UnknownFeature4,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Unknown 4'
        })
      ],
    });
  }

  onReadRequest(offset, callback) {
    trace('[UnknownCharacteristic4] onReadRequest');
    let buffer = new Buffer.alloc(1);
    buffer.writeUInt8(0xff);
    callback(this.RESULT_SUCCESS, buffer);
  }
}

module.exports = UnknownCharacteristic4;
