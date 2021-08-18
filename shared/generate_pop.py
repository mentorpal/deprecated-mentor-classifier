#
# This software is Copyright ©️ 2020 The University of Southern California. All Rights Reserved.
# Permission to use, copy, modify, and distribute this software and its documentation for educational, research and non-profit purposes, without fee, and without a written agreement is hereby granted, provided that the above copyright notice and subject to the full license file found in the root of this software deliverable. Permission to make commercial use of this software may be obtained by contacting:  USC Stevens Center for Innovation University of Southern California 1150 S. Olive Street, Suite 2300, Los Angeles, CA 90115, USA Email: accounting@stevens.usc.edu
#
# The full terms of this copyright and license should always be found in the root directory of this software deliverable as "license.txt" and if these terms are not found with this software, please contact the USC Stevens Center for the full license.
#
import urllib.request
from os import path
import json
from string import Template
import csv


def scrape_wiki(page: str, a):
    page = page.replace(" ", "%20")
    url_temp = Template(
        "https://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:$title&format=json&cmlimit=500"
    )
    url = url_temp.substitute({"title": page})
    pages = urllib.request.urlopen(url)
    data = json.load(pages)
    query = data["query"]
    category = query["categorymembers"]
    for x in category:
        a.add(x["title"])
    cont = None
    if "continue" in data.keys():
        cont = data["continue"]
    while cont:
        cont_str = cont["cmcontinue"]
        page_cont = url + "&cmcontinue=" + str(cont_str)
        pages = urllib.request.urlopen(page_cont)
        data = json.load(pages)
        query = data["query"]
        category = query["categorymembers"]
        for x in category:
            a.add(x["title"])
        if "continue" in data.keys():
            cont = data["continue"]
        else:
            break
    return a


pages = [
    "male characters in literature",
    "female characters in literature",
    "female characters in television",
    "male characters in television",
    "male characters in film",
    "female characters in film",
    "21st-century American singers",
    "20th-century American singers",
    "multinational food companies",
    "American brands",
    "20th-century American male actors",
    "20th-century American actresses",
    "American billionaires",
    "male characters in an animated series",
    "animated characters",
    "female characters in an animated series",
    "American comics characters",
    "American superheroes",
    "presidents of the United States",
]
a = set()
for page in pages:
    a = scrape_wiki(page, a)

file_path = path.abspath(path.join("installed", "pop_culture.csv"))
with open(file_path, "w") as f:
    write = csv.writer(f)
    for item in list(a):
        write.writerow([item])
