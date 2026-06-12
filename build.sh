#!/bin/bash

echo "=== 프론트엔드 빌드 ==="
cd frontend
npm install
npm run build

echo "=== 빌드 완료 ==="
