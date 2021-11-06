
SHELL = /bin/bash

all: build package

build:
	docker build --tag smartcartelambda:latest .

#Local Test
test:
	docker run \
		-w /var/task/ \
		--name smartcartelambda \
		--env AWS_ACCESS_KEY_ID=${SC_AWS_KEY} \
		--env AWS_SECRET_ACCESS_KEY=${SC_AWS_SECRET} \
 		--env AWS_REGION=us-east-1 \
		--env PYTHONPATH=/var/task \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		-itd \
		smartcartelambda:latest
	docker cp package.zip smartcartelambda:/tmp/package.zip
	docker exec -it smartcartelambda bash -c 'unzip -q /tmp/package.zip -d /var/task/'
	docker exec -it smartcartelambda bash -c 'pip3 install boto3 jmespath python-dateutil -t /var/task'
	docker exec -it smartcartelambda python3 -c 'from app.sentinel import APP; print(APP({"path": "/sentinel/search/", "queryStringParameters": "null", "pathParameters": "null", "requestContext": "null", "httpMethod": "GET"}, None))'
	docker stop smartcartelambda
	docker rm smartcartelambda


package:
	docker run \
		-w /var/task/ \
		--name smartcartelambda \
		-itd \
		smartcartelambda:latest
	docker cp smartcartelambda:/tmp/package.zip package.zip
	docker stop smartcartelambda
	docker rm smartcartelambda

shell:
	docker run \
		--name smartcartelambda  \
		--volume $(shell pwd)/:/data \
		--env PYTHONPATH=/var/task/vendored \
		--env GDAL_CACHEMAX=75% \
		--env GDAL_DISABLE_READDIR_ON_OPEN=TRUE \
		--env GDAL_TIFF_OVR_BLOCKSIZE=512 \
		--env VSI_CACHE=TRUE \
		--env VSI_CACHE_SIZE=536870912 \
		--rm \
		-it \
		smartcartelambda:latest /bin/bash

deploy:
	sls deploy

clean:
	docker stop smartcartelambda
	docker rm smartcartelambda
