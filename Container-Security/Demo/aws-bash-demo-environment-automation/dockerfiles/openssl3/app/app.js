const http = require('http');

const port = 80;

http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.write('Hello vulnerable World!');
  res.end();
}).listen(port);