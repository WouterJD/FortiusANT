const bleno = require('bleno');
const debug = require('debug')('fortiusant:fmcpc');

const RequestControl = 0x00;
const Reset = 0x01;
const SetTargetPower = 0x05;
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
const FitnessMachineControlPoint = '2AD9';

class FitnessMachineControlPointCharacteristic extends  bleno.Characteristic {
  constructor(messages, fmsc) {
    debug('[FitnessMachineControlPointCharacteristic] constructor')
    super({
      uuid: FitnessMachineControlPoint,
      properties: ['write', 'indicate'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Fitness Machine Control Point'
        })
      ]
    });

    this.messages = messages;
    this.fmsc = fmsc;
    this.indicate = null;

    this.hasControl = false;
    this.isStarted = false;
  }

  result(opcode, result) {
    let buffer = new Buffer.alloc(3);
    buffer.writeUInt8(ResponseCode);
    buffer.writeUInt8(opcode, 1);
    buffer.writeUInt8(result, 2);
    debug(buffer);
    return buffer;
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    debug('[FitnessMachineControlPointCharacteristic] onSubscribe');
    this.indicate = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    debug('[FitnessMachineControlPointCharacteristic] onUnsubscribe');
    this.indicate = null;
    return this.RESULT_UNLIKELY_ERROR;
  };

  onIndicate() {
    debug('[FitnessMachineControlPointCharacteristic] onIndicate');
  }

  onWriteRequest(data, offset, withoutResponse, callback) {
    debug('[FitnessMachineControlPointCharacteristic] onWriteRequest');

    // first byte indicates opcode
    let code = data.readUInt8(0);

    // when would it not be successful?
    callback(this.RESULT_SUCCESS);

    let response = null;

    switch(code){
      case RequestControl:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: RequestControl');
        if (this.hasControl) {
          debug('Warning: already has control');
        }
        else {
          this.hasControl = true;
          debug('Given control');
        }

        // Requesting control always succeeds
        response = this.result(code, Success);
        break;
      case Reset:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: Reset');
        if (this.hasControl) {
          debug('Control reset');
          this.hasControl = false;
          this.isStarted = false;
          response = this.result(code, Success);

          // Notify all connected clients that control has been reset
          this.fmsc.notifyReset();
        }
        else {
          debug('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case SetTargetPower:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: Set target power');
        if (this.hasControl) {
          let targetPower = data.readInt16LE(1);

          debug('Target Power(W): ' + targetPower);

          let message = {
            "target_power": targetPower
          }
          
          // Put in message fifo so FortiusANT can read it
          this.messages.push(message);

          response = this.result(code, Success);

          // Notify all connected clients about the new values
          this.fmsc.notifySetTargetPower(targetPower);
        }
        else {
          debug('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case StartOrResume:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: Start or Resume');
        if (this.hasControl) {
          if (this.isStarted) {
            debug('Error: already started/resumed');
            response = this.result(code, OperationFailed);
          }
          else {
            debug('started/resumed');
            this.isStarted = true;
            response = this.result(code, Success);

            // Notify all connected clients about the new state
            this.fmsc.notifyStartOrResume();
          }
        }
        else {
          debug('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case StopOrPause:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: Stop or Pause');
        if (this.hasControl) {
          if (this.isStarted) {
            debug('stopped');
            this.isStarted = false;
            response = this.result(code, Success);

            // Notify all connected clients about the new state
            this.fmsc.notifyStopOrPause();
          }
          else {
            debug('Error: already stopped/paused');
            response = this.result(code, OperationFailed);
          }
        }
        else {
          debug('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      case SetIndoorBikeSimulation:
        debug('[FitnessMachineControlPointCharacteristic] onWriteRequest: Set indoor bike simulation');
        if (this.hasControl) {
          let windSpeed = data.readInt16LE(1) * 0.001;
          let grade = data.readInt16LE(3) * 0.01;
          let crr = data.readUInt8(5) * 0.0001;
          let cw = data.readUInt8(6) * 0.01;

          debug('Wind speed(mps): ' + windSpeed);
          debug('Grade(%): ' + grade);
          debug('crr: ' + crr);
          debug('cw(Kg/m): ' + cw);

          let message = {
            "wind_speed": windSpeed,
            "grade": grade,
            "rolling_resistance_coefficient": crr,
            "wind_resistance_coefficient": cw
          }
          
          // Put in message fifo so FortiusANT can read it
          this.messages.push(message);

          response = this.result(code, Success);

          // Notify all connected clients about the new values
          this.fmsc.notifySetIndoorBikeSimulation(windSpeed, grade, crr, cw);
        }
        else {
          debug('Error: no control');
          response = this.result(code, ControlNotPermitted);
        }
        break;
      default:
        debug('Unsupported OPCODE:' + code);

        let d = new Buffer.from(data);
        debug('Data: ' + d);
        response = this.result(code, OpCodeNotSupported);
        break;
    }

    this.indicate(response);
  }
};

module.exports = FitnessMachineControlPointCharacteristic;
