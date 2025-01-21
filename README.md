This repository contains a python3 script that will convert a Track Shack PDF result file and convert it into a moldable CSV file to perform data analytics on.

The Track Shack runDisney races typically have a "Challenge" category which is a combination of two or more races with an aggregated time. runDisney does not
publish full results and rankings for the challenges. This script enables you to do that. 

To parse PDFs, it requires you install pymupdf4llm, which is a python3 library for parsing PDF documents into markdown text. It can be installed via _pip install pymupdf4llm_ on Linux or
Mac OS machines (or Windows with bash).

The code is written in python3. Sample input files can be found in the sample_files/ directory.

There is an option to import data from an existing markup file - this is mainly a debug feature.

Sample output files for previous races can be found in output/. 

Have fun, happy parsing and running.
