var bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:cpmc');

let CharacteristicUserDescription = '2901';
let ClientCharacteristicConfiguration = '2902';
let ServerCharacteristicConfiguration = '2903';
let CyclingPowerMeasurement = '2A63';

//https://developer.bluetooth.org/gatt/characteristics/Pages/CharacteristicViewer.aspx?u=org.bluetooth.characteristic.cycling_power_measurement.xml
class CyclingPowerMeasurementCharacteristic extends  bleno.Characteristic {
  constructor() {
    trace('[CyclingPowerMeasurementCharacteristic] constructor')
    super({
      uuid: CyclingPowerMeasurement,
      properties: ['notify'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Cycling Power Measurement'
        }),
        new bleno.Descriptor({
          uuid: ClientCharacteristicConfiguration,
          value: Buffer.alloc(2)
        }),
        new bleno.Descriptor({
          uuid: ServerCharacteristicConfiguration,
          value: Buffer.alloc(2)
        })
      ]
    });
    this.updateValueCallback = null;  
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    trace('[CyclingPowerMeasurementCharacteristic] onSubscribe');
    this.updateValueCallback = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    trace('[CyclingPowerMeasurementCharacteristic] onUnsubscribe');
    this.updateValueCallback = null;
    return this.RESULT_UNLIKELY_ERROR;
  };

  notify(event) {
    trace('[CyclingPowerMeasurementCharacteristic] notify');
    
    if (('watts' in event) || ('revolutions' in event)) {
      let buffer = new Buffer.alloc(8);

      if ('watts' in event) {
        let watts = event.watts;
        trace('[CyclingPowerMeasurementCharacteristic] power(W): ' + watts);
        buffer.writeInt16LE(watts, 2);
      }

      if ('revolutions' in event) {
        let CrankRevolutionDataPresent = 0x20;
        buffer.writeUInt16LE(CrankRevolutionDataPresent, 0);

        let revolutions = event.revolutions & 0xFFFF
        trace('[CyclingPowerMeasurementCharacteristic] revolutions: ' + revolutions);
        buffer.writeUInt16LE(revolutions, 4);

        let now = Date.now() * 1000 / 1024;
        let event_time = Math.floor(now) & 0xFFFF;
        trace('[CyclingPowerMeasurementCharacteristic] revolutions event time: ' + event_time);
        buffer.writeUInt16LE(event_time, 6);

        trace(buffer)
      }

      if (this.updateValueCallback) {
        this.updateValueCallback(buffer);
      }
    }

    return this.RESULT_SUCCESS;
  }
};

module.exports = CyclingPowerMeasurementCharacteristic;
