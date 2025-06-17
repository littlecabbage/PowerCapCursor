#!/bin/bash

# 设置变量
IMAGE_REGISTRY=${IMAGE_REGISTRY:-"your-registry.com"}
IMAGE_PROJECT=${IMAGE_PROJECT:-"powercap"}
VERSION=${VERSION:-$(git describe --tags --always)}
API_IMAGE_NAME="${IMAGE_REGISTRY}/${IMAGE_PROJECT}/powercap-api"
WORKER_IMAGE_NAME="${IMAGE_REGISTRY}/${IMAGE_PROJECT}/powercap-worker"

# 构建API镜像
echo "Building API image..."
docker build -t "${API_IMAGE_NAME}:${VERSION}" -f Dockerfile.api .
docker tag "${API_IMAGE_NAME}:${VERSION}" "${API_IMAGE_NAME}:latest"

# 构建Worker镜像
echo "Building Worker image..."
docker build -t "${WORKER_IMAGE_NAME}:${VERSION}" -f Dockerfile.worker .
docker tag "${WORKER_IMAGE_NAME}:${VERSION}" "${WORKER_IMAGE_NAME}:latest"

# 如果提供了PUSH=true参数，则推送镜像
if [ "${PUSH}" = "true" ]; then
    echo "Pushing images to registry..."
    docker push "${API_IMAGE_NAME}:${VERSION}"
    docker push "${API_IMAGE_NAME}:latest"
    docker push "${WORKER_IMAGE_NAME}:${VERSION}"
    docker push "${WORKER_IMAGE_NAME}:latest"
fi

echo "Build completed successfully!"
echo "API Image: ${API_IMAGE_NAME}:${VERSION}"
echo "Worker Image: ${WORKER_IMAGE_NAME}:${VERSION}" 