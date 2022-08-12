var AWS = require('aws-sdk');

exports.handler = function(event, context, callback) {
    console.log('Received event:', JSON.stringify(event.Records[0].Sns.Message, null, 4));

    var message = JSON.parse(event.Records[0].Sns.Message);
    //console.log('Message received from SNS:', message);
    console.log('bucket: ' + message.bucket);
    console.log('file: ' + message.file);
    var params = {
      Bucket: message.bucket,
      Key: message.file
    };
    var s3 = new AWS.S3();
    s3.deleteObject(params, function(err, data) {
      if (err) console.log(err, err.stack); // an error occurred
      else     console.log(data);           // successful response
      /*
      data = {
      }
      */
    });
    callback(null, message);
};