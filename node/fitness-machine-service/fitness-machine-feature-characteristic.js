const bleno = require('bleno');
const debug = require('debug')('fortiusant:fmfc');

function bit(nr) {
  return (1 << nr);
}

const CadenceSupported = bit(1);
const HeartRateMeasurementSupported = bit(10);
const PowerMeasurementSupported = bit(14);

const PowerTargetSettingSupported = bit(3);
const IndoorBikeSimulationParametersSupported = bit(13);

const CharacteristicUserDescription = '2901';
const FitnessMachineFeature = '2ACC';

class FitnessMachineFeatureCharacteristic extends  bleno.Characteristic {
  constructor() {
    debug('[FitnessMachineFeatureCharacteristic] constructor');
    super({
      uuid: FitnessMachineFeature,
      properties: ['read'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Fitness Machine Feature'
        })
      ],
    });
  }

  onReadRequest(offset, callback) {
    debug('[FitnessMachineFeatureCharacteristic] onReadRequest');
    let flags = new Buffer.alloc(8);
    flags.writeUInt32LE(CadenceSupported | PowerMeasurementSupported);
    flags.writeUInt32LE(IndoorBikeSimulationParametersSupported | PowerTargetSettingSupported, 4);
    callback(this.RESULT_SUCCESS, flags);
  }
}

module.exports = FitnessMachineFeatureCharacteristic;
