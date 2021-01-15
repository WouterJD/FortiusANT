const bleno = require('bleno');
const events = require('events');
const debug = require('debug')('fortiusant:vt');

const FitnessMachineService = require('./fitness-machine-service/fitness-machine-service');
const HeartRateService = require('./heart-rate-service/heart-rate-service');
const SteeringService = require('./steering-service/steering-service');

class VirtualTrainer extends events {
  constructor(steeringEnabled) {
    debug('[VirtualTrainer] constructor');
    super();

    this.name = 'FortiusANT Trainer';
    process.env['BLENO_DEVICE_NAME'] = this.name;
    
    this.messages = [];
    this.ftms = new FitnessMachineService(this.messages);
    this.hrs = new HeartRateService();
    this.ss = new SteeringService();
    this.stopTimer = null;
    this.steeringEnabled = steeringEnabled;
    
    bleno.on('stateChange', (state) => {
      debug(`[${this.name}] stateChange: ${state}`);
      
      if (state === 'poweredOn') {
        let uuids = [
          this.ftms.uuid,
          this.hrs.uuid
        ]

        if (this.steeringEnabled) {
          uuids.push(this.ss.uuid)
        }

        bleno.startAdvertising(this.name, uuids);
      }
      else {
        debug(`[${this.name}] Stopping...`);
        bleno.stopAdvertising();
      }
    });

    bleno.on('advertisingStart', (error) => {
      debug(`[${this.name}] advertisingStart: ${(error ? 'error ' + error : 'success')}`);

      if (!error) {
        let services = [
          this.ftms,
          this.hrs
        ]

        if (this.steeringEnabled) {
          services.push(this.ss)
        }

        bleno.setServices(services,
        (error) => {
          debug(`[${this.name}] setServices: ${(error ? 'error ' + error : 'success')}`);
        });
      }
    });

    bleno.on('advertisingStartError', () => {
      debug(`[${this.name}] advertisingStartError: advertising stopped`);
    });

    bleno.on('advertisingStop', error => {
      debug(`[${this.name}] advertisingStop: ${(error ? 'error ' + error : 'success')}`);
    });

    bleno.on('servicesSet', error => {
      debug(`[${this.name}] servicesSet: ${(error ? 'error ' + error : 'success')}`);
    });

    bleno.on('accept', (clientAddress) => {
      debug(`[${this.name}] accept: client ${clientAddress}`);
      bleno.updateRssi();
    });

    bleno.on('rssiUpdate', (rssi) => {
      debug(`[${this.name}] rssiUpdate: ${rssi}')}`);
    });
  }

  get() {
    debug(`[${this.name}] get')}`);
    data = this.messages.shift();
    if (typeof data === 'undefined') {
      debug(`[${this.name}] get: no messages in queue')}`);
      data = {};
    }
    return data;
  }

  update(event) {
    debug(`[${this.name}] update: ${JSON.stringify(event)}`);
    
    if (this.stopTimer) {
      clearTimeout(this.stopTimer);
    }

    this.ftms.notify(event);
    this.hrs.notify(event);
    if (this.steeringEnabled) {
      this.ss.notify(event);
    }

    if (!('stop' in event)) {
      this.stopTimer = setTimeout(() => {
        debug(`[${this.name}] send stop`);
        this.update({
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
