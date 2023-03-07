
const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:rx');

const CharacteristicUserDescription = '2901';
const UnknownFeature1 = '347b0031-7635-408b-8918-8ff3949ce592';

class RxCharacteristic extends  bleno.Characteristic {
  constructor(tc) {
    trace('[RxCharacteristic] constructor');
    super({
      uuid: UnknownFeature1,
      properties: ['write'],
      //descriptors: [
      //  new bleno.Descriptor({
      //    uuid: CharacteristicUserDescription,
      //    value: 'Rx'
      //  })
      //],
    });

    this.tc = tc;
  }

  onWriteRequest(data, offset, withoutResponse, callback) {
    trace('[RxCharacteristic] onWriteRequest');
    trace('data len: ' + data.length);

    if (data.length == 1) {
      let value = data.readUInt8(0);
      trace('data: ' + value);
      callback(this.RESULT_SUCCESS);
      return;
    }

    let value = data.readUInt16BE(0);
    trace('[RxCharacteristic] write ' + value);

    switch(value) {
      case 0x0312:
        if (data.length < 6) {
          trace('[RxCharacteristic] Challenge too short');
          break;
        }

        if (this.tc.indicate) {
          let x = data.readUInt32LE(2);
          trace('[RxCharacteristic] Received challenge (0x' + x.toString(16) + ')');

          let k = 0x16fa5717;
          let d = x % 11;
          let rot_x = ((x << d) | (x >>> (32-d))) >>> 0;
          let y = (rot_x ^ (x + k)) >>> 0;

          trace('[RxCharacteristic] Calculated response (0x' + y.toString(16) + ')');

          let buffer = new Buffer.alloc(6);
          buffer.writeUInt16BE(0x0312, 0);
          buffer.writeUInt32LE(y, 2);
          trace('[RxCharacteristic] Indicating (' + buffer + ') via tx characteristic');
          this.tc.indicate(buffer);
        }
        else {
          trace('[RxCharacteristic] Cannot indicate, no callback registered');
        }
        break;
      case 0x0313:
        if (this.tc.indicate) {
          trace('[RxCharacteristic] Response received, acknowledging');

          let buffer = new Buffer.alloc(3);
          buffer.writeUInt16BE(0x0313, 0);
          buffer.writeUInt8(0xff, 2);
          trace('[RxCharacteristic] Indicating (' + buffer + ') via tx characteristic');
          this.tc.indicate(buffer);
        }
        else {
          trace('[RxCharacteristic] Cannot indicate, no callback registered');
        }
        break;
      case 0x0202:
        trace('[RxCharacteristic] Received 0x0202');
        break;
      default:
        trace('[RxCharacteristic] Unknown value: ' + value);
        break;
    }

    callback(this.RESULT_SUCCESS);
  }
}

module.exports = RxCharacteristic;
