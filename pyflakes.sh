#!/bin/bash

echo "============================================================"
echo "== pyflakes =="
pyflakes dform | grep -v migration
