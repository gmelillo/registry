#!/bin/bash

env

for i in $(seq 1 5); do echo "iteration" $i; sleep 3; done
