#!/bin/sh
pdm run coverage run -m pytest
pdm run coverage report -m
pdm run coverage xml