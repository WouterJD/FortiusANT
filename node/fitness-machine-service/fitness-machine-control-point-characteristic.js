const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:fmcpc');

const RequestControl = 0x00;
const Reset = 0x01;
const StartOrResume = 0x07;
const StopOrPause = 0x08;
const SetIndoorBikeSimulation = 0x11;
const ResponseCode = 0x80;

const Success = 0x01;
const OpCodeNotSupported = 0x02;
const InvalidParameter = 0x03;
const OperationFailed = 0x04;
const ControlNotPermitted = 0x05;

const CharacteristicUserDescription = '2901';
const ClientCharacteristicConfiguration = '2902';
const ServerCharacteristicConfiguration = '2903';
const FitnessMachineControlPoint = '2AD9';

class FitnessMachineControlPointCharacteristic extends  bleno.Characteristic {
  constructor(messages) {
    trace('[FitnessMachineControlPointCharacteristic] constructor')
    super({
      uuid: FitnessMachineControlPoint,
      properties: ['write', 'indicate'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Fitness Machine Control Point'
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

    this.messages = messages;
    this.indicate = null;

    this.hasControl = false;
    this.isStarted = false;
  }

  result(opcode, result) {
    let buffer = new Buffer.alloc(3);
    buffer.writeUInt8(ResponseCode);
    buffer.writeUInt8(opcode, 1);
    buffer.writeUInt8(result, 2);
    trace(buffer);
    return buffer;
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    trace('[FitnessMachineControlPointCharacteristic] onSubscribe');
    this.indicate = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    trace('[FitnessMachineControlPointCharacteristic] onUnsubscribe');
    this.indicate = null;
    return this.RESULT_UNLIKELY_ERROR;
  };

  onIndicate() {
    trace('[FitnessMachineControlPointCharacteristic] onIndicate');
  }

  onWriteRequest(data, offset, withoutResponse, callback) {
    trace('[FitnessMachineControlPointCharacteristic] onWriteRequest');

    // first byte indicates opcode
    let code = data.readUInt8(0);

    // when would it not be successful?
    callback(this.RESULT_SUCCESS);

    let response = null;

    switch(code){
      case RequestControl:
        trace('[FitnessMachineControlPointCharacteristic] onWriteRequest: RequestControl');
        if (this.hasControl) {
          trace('Error: already has control');
          response = this.result(code, ControlNotPermitted);
        }
        else {
          trace('Given control');
          this.hasControl = true;
          response = this.result(code, Success);
        }
        break;
      case Reset:
        trace('[FitnessMachineControlPointCharacteristic] onWriteRequest: Reset');
        if (this.hasControl) {
          trace('Control reset');
          this.hasControl = false;
          response = this.result(code, Success);
        }
        else {
          trace('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case StartOrResume:
        trace('[FitnessMachineControlPointCharacteristic] onWriteRequest: Start or Resume');
        if (this.hasControl) {
          if (this.isStarted) {
            trace('Error: already started/resumed');
            response = this.result(code, OperationFailed);
          }
          else {
            trace('started/resumed');
            this.isStarted = true;
            response = this.result(code, Success);
          }
        }
        else {
          trace('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case StopOrPause:
        trace('[FitnessMachineControlPointCharacteristic] onWriteRequest: Stop or Pause');
        if (this.hasControl) {
          if (this.isStarted) {
            trace('stopped');
            this.isStarted = false;
            response = this.result(code, Success);
          }
          else {
            trace('Error: already stopped/paused');
            response = this.result(code, OperationFailed);
          }
        }
        else {
          trace('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case SetIndoorBikeSimulation:
        trace('[FitnessMachineControlPointCharacteristic] onWriteRequest: Set indoor bike simulation');
        if (this.hasControl) {
          let windSpeed = data.readInt16LE(1) * 0.001;
          let grade = data.readInt16LE(3) * 0.01;
          let crr = data.readUInt8(5) * 0.0001;
          let cw = data.readUInt8(6) * 0.01;

          trace('Wind speed(mps): ' + windSpeed);
          trace('Grade(%): ' + grade);
          trace('crr: ' + crr);
          trace('cw(Kg/m): ' + cw);

          let message = {
            "wind_speed": windSpeed,
            "grade": grade,
            "rolling_resistance_coefficient": crr,
            "wind_resistance_coefficient": cw
          }
          
          // Put in message fifo so FortiusANT can read it
          this.messages.push(message);

          response = this.result(code, Success);
        }
        else {
          trace('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      default:
        // Unsupported opcode
        trace('len: ' + data.length);
        let d = new Buffer.from(data);
        trace(d);
        response = this.result(code, OpCodeNotSupported);
        break;
    }

    this.indicate(response);
  }
};

module.exports = FitnessMachineControlPointCharacteristic;