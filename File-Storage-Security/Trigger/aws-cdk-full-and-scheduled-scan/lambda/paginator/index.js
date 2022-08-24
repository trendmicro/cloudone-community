const AWS = require('aws-sdk');
const s3 = new AWS.S3();

const STATE_BUCKET = process.env.STATE_BUCKET;
const KEY_WITH_KEYS_TO_SCAN ='keys';

exports.lambda_handler = async (event) => {
  console.log(event);
  const bucket = event.bucket;
  const allKeys = await getAllKeys(bucket);
  const writeResult = await writeToBucket(allKeys, KEY_WITH_KEYS_TO_SCAN, STATE_BUCKET);

  return {
    bucket: bucket,
    stateBucket: STATE_BUCKET,
    stateKey: KEY_WITH_KEYS_TO_SCAN,
    limit: 500
  }
};

const getKeysInPage = async (bucket, continuationToken) => {
  const params = {
    Bucket: bucket,
    ContinuationToken: continuationToken? continuationToken : null
  };
  const response = await s3.listObjectsV2(params).promise();
  return {
    keys: response.Contents.map(object => object.Key),
    nextContinuationToken: response.NextContinuationToken
  };
};

const getAllKeys = async (bucket) => {
  let {keys, nextContinuationToken} = await getKeysInPage(bucket);
  while (nextContinuationToken){
    const result = await getKeysInPage(bucket, nextContinuationToken);
    console.log(result);
    keys.push(...result.keys);
    nextContinuationToken = result.nextContinuationToken? result.nextContinuationToken : null;
  }
  return keys;
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
  