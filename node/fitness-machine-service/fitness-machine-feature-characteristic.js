const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:fmfc');

function bit(nr) {
  return (1 << nr);
}

const CadenceSupported = bit(1);
const HeartRateMeasurementSupported = bit(10);
const PowerMeasurementSupported = bit(14);

// TODO: should targetting be used to actually control the resistance? Which one to choose
const ResistanceTargetSettingSupported = 0x04;
const PowerTargetSettingSupported = 0x08;

const CharacteristicUserDescription = '2901';
const FitnessMachineFeature = '2ACC';

class FitnessMachineFeatureCharacteristic extends  bleno.Characteristic {
  constructor() {
    trace('[FitnessMachineFeatureCharacteristic] constructor');
    let flags = new Buffer.alloc(8);
    // TODO: should this be configurable? e.g. no heartrate support?
    // For now, only support cadence and power measurement
    flags.writeUInt32LE(CadenceSupported | HeartRateMeasurementSupported | PowerMeasurementSupported);
    // TODO: which targetting feature should be used?
    flags.writeUInt32LE(0, 4);

    super({
      uuid: FitnessMachineFeature,
      value: flags,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Fitness Machine Feature'
        })
      ],
    });
  }
}

module.exports = FitnessMachineFeatureCharacteristic;
