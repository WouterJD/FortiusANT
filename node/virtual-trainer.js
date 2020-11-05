const bleno = require('bleno');
const events = require('events');
const debug = require('debug');
const trace = debug('fortiusant:vt');

const CyclingPowerService = require('./cycling-power-service/cycling-power-service');

class VirtualTrainer extends events {
  constructor() {
    trace('[VirtualTrainer] constructor');
    super();

    this.name = 'VirtualTrainer';
    process.env['BLENO_DEVICE_NAME'] = this.name;

    this.csp = new CyclingPowerService();
    // this.dis = TODO

    this.last_revolutions = 0;
    this.last_csp_time = 0;
    this.timer = null;

    bleno.on('stateChange', (state) => {
      trace(`[${this.name}] stateChange: ${state}`);
      
      if (state === 'poweredOn') {
        bleno.startAdvertising(this.name, [
          // this.dis.uuid,
          this.csp.uuid
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
          // this.dis,
          this.csp
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

  updateCSP(event) {
    trace(`[${this.name}] updateCSP: ${JSON.stringify(event)}`);
    
    // Clear the timer since we received a new update
    if (this.timer) {
      clearTimeout(this.timer);
    }

    this.csp.notify(event);

    if ('watts' in event) {
      if ('revolutions' in event) {
        this.last_revolutions = event.revolutions
      }
      this.last_csp_time = Date.now();
    }
    else {
      trace(`[${this.name}] updateCSP: watt value missing in event`)
    }

    // Set a timer to send a message when no more updates are received
    this.timer = setTimeout(() => {
      this.updateCSP({
        'watts': 0,
        'revolutions': this.revolutions
      })
    }, 1500);
  }
}

module.exports = VirtualTrainer;
