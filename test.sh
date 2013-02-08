#!/bin/bash
cd test_project
./manage.py jenkins xapp_render
cd ..
rm -r reports
mv test_project/reports .
