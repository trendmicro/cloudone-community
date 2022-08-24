const AWS = require('aws-sdk');
const s3 = new AWS.S3();

const fetchKeys = async (bucket, key) => {
    try {
        const params = {
            Bucket: bucket,
            Key: key
        };
        const result = await s3.getObject(params).promise();
        const keys = JSON.parse(result.Body.toString('utf-8'));
        return keys;
    } catch (error) {
        throw error;
    }
};

const writeToBucket = async (content, key, bucket) => {
    try {
      const params = {
        Bucket: bucket,
        Key: key,
        ContentType:'binary',
        Body: Buffer.from(JSON.stringify(content))
      };
      const result = await s3.putObject(params).promise();
      return result;
    } catch (error) {
      return error;
    }
};

const filterKeys = (keys, limit) => {
    const keysToScan = keys.slice(0, limit);
    const remainingKeys = keys.slice(limit);
    return {
        keysToScan,
        remainingKeys
    };
};

exports.lambda_handler = async (event) => {
    console.log(event);
    const stateBucket = event.stateBucket;
    const stateKey = event.stateKey;
    const scanLimitPerIteration = event.limit;
    const bucket = event.bucket;
    const allKeys = await fetchKeys(stateBucket, stateKey);
    
    const filtered = filterKeys(allKeys, scanLimitPerIteration);
    
    // Rewrite file in bucket with remaining keys
    if (filtered.remainingKeys){
        await writeToBucket(filtered.remainingKeys, stateKey, stateBucket);
    }

    const response = {
        keys: filtered.keysToScan,
        bucket: bucket,
        limit: scanLimitPerIteration,
        remainingKeysLength: filtered.remainingKeys? filtered.remainingKeys.length : null,
        stateBucket: event.stateBucket,
        stateKey: event.stateKey
    };
    
    return response;
};
