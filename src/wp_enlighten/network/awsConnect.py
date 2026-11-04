import boto3

client = boto3.client("cognito-identity", region_name="us-east-1")

response = client.get_id(
    IdentityPoolId="us-east-1:93d19108-8553-4ce6-ad24-4f39f097ddc4",
)

response_cred = client.get_credentials_for_identity(
    IdentityId=response["IdentityId"],
)

access_id = response_cred["Credentials"]["AccessKeyId"]
access_secret = response_cred["Credentials"]["SecretKey"]
access_session = response_cred["Credentials"]["SessionToken"]
print(response_cred["Credentials"].keys())
print(response_cred)

s3_session = boto3.Session(
    aws_access_key_id=access_id,
    aws_secret_access_key=access_secret,
    aws_session_token=access_session,
)

s3_resource = s3_session.resource("s3")

eeprom_bucket = s3_resource.Bucket("eeprom-factory-files")

for my_bucket_object in eeprom_bucket.objects.all():
    print(my_bucket_object.key)
