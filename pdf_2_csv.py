#!/usr/bin/env python3

import PyPDF2
import sys
import re

def processPdf(filename):
    f = open(filename,"rb")

    reader = PyPDF2.PdfFileReader(f)
    
    cstart = 0
    cfinish = 0
    contents = []
    
    # Get table of contents
    for page in reader.pages:
        if "Recommendations" in page.extractText():
            cstart = reader.getPageNumber(page)
        if "Appendix" in page.extractText():
            cfinish = reader.getPageNumber(page) + 1
            break
    
    rows = []
    for i in range(cstart,cfinish):
        rows += reader.getPage(i).extractText().split("\n")

    item = ""
    # Find pages for each item
    for i,row in enumerate(rows):
        m = re.match("[0-9]+\.([0-9]+\.?)+",row)
        if m != None:
            for line in rows[i:]:
                item += line.replace(m.group(0),"",1)
                n = re.match("^[0-9]+$",line)
                if n != None:
                    contents.append({"Ref":m.group(0),"page":int(n.group(0)),"title":item[:item.find(".")]})
                    item = ""
                    break

    table = {}

    # Extract rationale for each finding
    for item in contents:
        pageText = ""
        while not "Rationale" in pageText:
            pageText = reader.getPage(item["page"]).extractText()
            item["page"] += 1
        lines = pageText.split("\n")
        rationale = ""
        s = False
        for line in lines:
            if "Rationale" in line:
                s = True
            elif "Audit" in line:
                break
            elif s:
                rationale += line
        
        table[item['Ref']] = {"Ref": item['Ref'],"Rationale": rationale, "Requirement": item['title'], "Current": "Pass"}

    f.close()
    return table

if __name__ ==  "__main__":
    print("Ref,Requirement,Rationale,Current")
    table = processPdf(sys.argv[1])
    for row in table:
        print('"{}","{}","{}","{}"\r\n'.format(row,table[row]["Requirement"],table[row]["Rationale"],table[row]["Current"]))

