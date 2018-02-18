alexa:
	cd lambda; \
	zip -r ../lambda.zip *
	aws lambda update-function-code --function-name alexaHomeSecurity --zip-file fileb://lambda.zip