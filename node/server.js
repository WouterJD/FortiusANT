const VirtualTrainer = require("./virtual-trainer");
const express = require('express');
const bodyParser = require('body-parser');
const debug = require('debug');
const trace = debug('fortiusant:server');

let Trainer = new VirtualTrainer();
let server = express();

server.use(bodyParser.urlencoded({extended: true}));

server.listen(9999, function() {
  trace('[Server] listen: running on port 9999');
})

server.post('/ant', function(req, res) {
  res.send();
  data = req.body
  trace(`[Server] post: /ant : ${JSON.stringify(data)}`);
  Trainer.update(data);
});
