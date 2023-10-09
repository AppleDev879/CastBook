import AWS from "aws-sdk";
import { v4 as uuidv4 } from "uuid";

const s3 = new AWS.S3();

export const handler = async (event) => {
  // Get the S3 bucket name from an environment variable
  const environment = event.headers["X-Environment"] || "test";
  const bucketName = environment + "-" + process.env.S3_BUCKET_NAME;

  // Generate a UUID as the object key
  const objectKey = uuidv4();

  // Define parameters for generating the pre-signed URL
  const params = {
    Bucket: bucketName,
    Key: objectKey,
    Expires: 5 * 60, // URL expires in 5 minutes (adjust as needed)
    ContentType: "application/pdf", // Set the content type as PDF
  };

  try {
    // Generate the pre-signed URL
    const url = await s3.getSignedUrlPromise("putObject", params);

    // Return the pre-signed URL in the response
    return {
      statusCode: 200,
      body: JSON.stringify({ uploadURL: url, docKey: objectKey }),
    };
  } catch (error) {
    console.error("Error generating pre-signed URL:", error);
    return {
      statusCode: 500,
      body: JSON.stringify({ error: "Internal Server Error" }),
    };
  }
};
