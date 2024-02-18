#!/bin/sh

cd src && \
    pdm run python -m tests.test_$1 & \
    cd .. 