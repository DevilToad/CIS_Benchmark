#!/usr/bin/env python3

import csv
import re
import pdf_2_csv
import argparse

parser = argparse.ArgumentParser(description="Process Nessus output for CIS Benchmarks")
parser.add_argument('-n', help='The Nessus file to process in CSV format')
parser.add_argument('-p', help='PDF Benchmark file')

args = parser.parse_args()

benchmark = pdf_2_csv.processPdf(args.p)

findings = []

with open(args.n) as f:
    reader = csv.DictReader(f)
    findings = [row for row in reader if "Compliance Checks" in row['Name'] and "[FAILED]" in row['Description']]

for i,row in enumerate(findings):
    m = re.search("^\"[1-9\.]+",row['Description'])
    fid = m.group(0)[1:].strip()
    m = re.search("Remote value:",row['Description'])
    n = re.search("Policy value: .+$",row['Description'])
    try:
        remote = row['Description'][m.span()[1]:n.span()[0]].replace("\n","\r\n")
    except AttributeError:
        print("couldn't read finding {}: {}".format(i,row['Description'][:10]))
        continue
    try:
        benchmark[fid]['Current'] = remote
    except KeyError:
        print("Couldn't find benchmark item {}".format(fid))
        continue

with open("output.csv",'w') as f:
    fieldnames = ['Ref','Requirement','Rationale','Current']
    writer = csv.DictWriter(f,fieldnames=fieldnames)
    for row in benchmark:
        writer.writerow(benchmark[row])
