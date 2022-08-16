const bleno = require('bleno');

const SteeringCharacteristic = require('./steering-characteristic');
const RxCharacteristic = require('./rx-characteristic');
const TxCharacteristic = require('./tx-characteristic');
const UnknownCharacteristic1 = require('./unknown-characteristic-1');
const UnknownCharacteristic2 = require('./unknown-characteristic-2');
const UnknownCharacteristic3 = require('./unknown-characteristic-3');
const UnknownCharacteristic4 = require('./unknown-characteristic-4');

const Steering = "347b0001-7635-408b-8918-8ff3949ce592";

class SteeringService extends bleno.PrimaryService {
  constructor() {
    let uc1 = new UnknownCharacteristic1();
    let uc2 = new UnknownCharacteristic2();
    let uc3 = new UnknownCharacteristic3();
    let uc4 = new UnknownCharacteristic4();
    let sc = new SteeringCharacteristic();
    let tc = new TxCharacteristic();
    let rc = new RxCharacteristic(tc);
    super({
      uuid: Steering,
      characteristics: [
        uc1,
        uc2,
        uc3,
        uc4,
        sc,
        rc,
        tc
      ]
    });
    
    this.uc1 = uc1;
    this.uc2 = uc2;
    this.uc3 = uc3;
    this.uc4 = uc4;
    this.sc = sc;
    this.rc = rc;
    this.tc = tc;
  }

  notify(event) {
    this.sc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = SteeringService;
