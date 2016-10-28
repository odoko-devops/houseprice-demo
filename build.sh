#!/bin/sh

if [ -z $VERSION ]; then
  if [ "$1" = "push" ]; then
    VERSION=1.0.$BUILD_NUMBER
  else
    VERSION=latest
  fi
fi

REG=docker.odoko.org

echo "Building $VERSION"
docker build -t $REG/houseprices:${VERSION} .
if [ "$1" = "push" ]; then
  echo "Pushing $VERSION..."
  docker push $REG/houseprices:${VERSION}
fi
