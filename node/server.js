const VirtualTrainer = require("./virtual-trainer");
const express = require('express');
const bodyParser = require('body-parser');
const debug = require('debug');
const trace = debug('fortiusant:server');

let trainer = new VirtualTrainer();
let server = express();

server.use(bodyParser.urlencoded({extended: true}));

server.listen(9999, function() {
  debug('[Server] listen: running on port 9999');
})

server.post('/ant', function(req, res) {
  res.send();
  data = req.body
  debug(`[Server] post: /ant : ${JSON.stringify(data)}`);
  trainer.update(data);
});

server.get('/ant', function(req, res) {
  data = trainer.get();
  debug(`[Server] get: /ant : ${JSON.stringify(data)}`);
  res.send(data)
});
