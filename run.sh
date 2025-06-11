#!/bin/bash

skaffold deploy -p test \
                --images=app-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-crawler:34d2ec6",aws-image="europe-west4-docker.pkg.dev/gcp-automated-blog-test/autoblog-test-gar/blog-ai-assistant-aws-tunnel:fef2779"