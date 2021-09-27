import logging
import json
import boto3
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

endpoint_url = os.environ['ENDPOINT_URL']     # 環境変数よりMedia Convertエンドポイント取得
mediaconvert_client =  boto3.client('mediaconvert', region_name='ap-northeast-1',endpoint_url= endpoint_url)

def lambda_handler(event, context):
    s3_input_bucket = event['Records'][0]['s3']['bucket']['name']                   # S3イベント通知よりバケット名取得
    s3_key = event['Records'][0]['s3']['object']['key']                             # S3イベント通知よりキー名取得
    output_bucket = os.environ['OUTPUT_BUCKET']                                     # 環境変数より出力先バケット取得
    media_convert_job_template_arn = os.environ['MEDIA_CONVERT_JOB_TEMPLATE_ARN']   # 環境変数よりジョブテンプレートARN取得
    media_convert_role_arn = os.environ['MEDIA_CONVERT_ROLE_ARN']                   # 環境変数よりMediaConvertジョブ実行時に指定するIAMロールARN取得
    media_convert_que = os.environ['MEDIA_CONVERT_QUE']                             # 環境変数よりMediaConvertキュー取得

    # ハンドラーに渡されたイベントデータをロギング(デバッグ)
    logger.debug("EVENT: " + json.dumps(event))
    input_file = 's3://{0}/{1}'.format(s3_input_bucket,s3_key)
    output_file = 's3://{0}/'.format(output_bucket)

    try:
        with open("job.json", "r") as jsonfile:
            job_object = json.load(jsonfile)
            
        job_object["OutputGroups"][0]["OutputGroupSettings"]["HlsGroupSettings"]["Destination"] = output_file
        job_object["Inputs"][0]["FileInput"] = input_file

        response = mediaconvert_client.create_job(
          JobTemplate = media_convert_job_template_arn,
          Queue = media_convert_que,
          Role = media_convert_role_arn,
          Settings=job_object
        )
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(s3_key, s3_input_bucket))
        raise e