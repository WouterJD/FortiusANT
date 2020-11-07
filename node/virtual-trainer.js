const bleno = require('bleno');
const events = require('events');
const debug = require('debug');
const trace = debug('fortiusant:vt');

const FitnessMachineService = require('./fitness-machine-service/fitness-machine-service');
const HeartRateService = require('./heart-rate-service/heart-rate-service');

class VirtualTrainer extends events {
  constructor() {
    trace('[VirtualTrainer] constructor');
    super();

    this.name = 'VirtualTrainer';
    process.env['BLENO_DEVICE_NAME'] = this.name;

    this.ftms = new FitnessMachineService();
    this.hrs = new HeartRateService();

    this.stopTimer = null;

    bleno.on('stateChange', (state) => {
      trace(`[${this.name}] stateChange: ${state}`);
      
      if (state === 'poweredOn') {
        bleno.startAdvertising(this.name, [
          this.ftms.uuid,
          this.hrs.uuid
        ]);
      }
      else {
        trace(`[${this.name}] Stopping...`);
        bleno.stopAdvertising();
      }
    });

    bleno.on('advertisingStart', (error) => {
      trace(`[${this.name}] advertisingStart: ${(error ? 'error ' + error : 'success')}`);

      if (!error) {
        bleno.setServices([
          this.ftms,
          this.hrs
        ],
        (error) => {
          trace(`[${this.name}] setServices: ${(error ? 'error ' + error : 'success')}`);
        });
      }
    });

    bleno.on('advertisingStartError', () => {
      trace(`[${this.name}] advertisingStartError: advertising stopped`);
    });

    bleno.on('advertisingStop', error => {
      trace(`[${this.name}] advertisingStop: ${(error ? 'error ' + error : 'success')}`);
    });

    bleno.on('servicesSet', error => {
      trace(`[${this.name}] servicesSet: ${(error ? 'error ' + error : 'success')}`);
    });

    bleno.on('accept', (clientAddress) => {
      trace(`[${this.name}] accept: client ${clientAddress}`);
      bleno.updateRssi();
    });

    bleno.on('rssiUpdate', (rssi) => {
      trace(`[${this.name}] rssiUpdate: ${rssi}')}`);
    });
  }

  update(event) {
    trace(`[${this.name}] update: ${JSON.stringify(event)}`);
    
    if (this.stopTimer) {
      clearTimeout(this.stopTimer);
    }

    this.ftms.notify(event);
    this.hrs.notify(event);

    if (!('stop' in event)) {
      this.stopTimer = setTimeout(() => {
        trace(`[${this.name}] send stop`);
        this.updateCSP({
          'watts': 0,
          'cadence': 0,
          'heart_rate': 0,
          'stop': true
        })
      }, 1500);
    }
  }
}

module.exports = VirtualTrainer;
