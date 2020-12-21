
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
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Rx'
        })
      ],
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
      case 0x0310:
        if (this.tc.indicate) {
          let buffer = new Buffer.alloc(4);
          buffer.writeUInt16BE(0x0310, 0);
          buffer.writeUInt16BE(0x4a89, 2);
          trace('[RxCharacteristic] Indicating (' + buffer + ') via tx characteristic');
          this.tc.indicate(buffer);
        }
        else {
          trace('[RxCharacteristic] Cannot indicate, no callback registered');
        }
        break;
      case 0x0311:
        if (this.tc.indicate) {
          let buffer = new Buffer.alloc(4);
          buffer.writeUInt16BE(0x0311, 0);
          buffer.writeUInt16BE(0xffff, 2);
          trace('[RxCharacteristic] Indicating (' + buffer + ') via tx characteristic');
          this.tc.indicate(buffer);
        }
        else {
          trace('[RxCharacteristic] Cannot indicate, no callback registered');
        }
        break;
      case 0x0202:
        trace('[RxCharacteristic] Received 0x0202');
      default:
        trace('[RxCharacteristic] Unknown value: ' + value);
        break;
    }

    callback(this.RESULT_SUCCESS);
  }
}

module.exports = RxCharacteristic;
