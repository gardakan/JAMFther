import pdftotext
import re
import datetime
import pandas as pd
import tkinter as tk
import numpy as np
from tkinter.filedialog import asksaveasfile
from tkinter import ttk, IntVar, filedialog, Checkbutton, Listbox

# Dict with regex match strings for desired fields
searchStrings = {
    "Date":             "\d+/\d+/\d+",
    "Invoice":          "^5[0-9]{4}",
    "Serial number":    "^FVFC\w\w\w\wMNHX",
    "Billing amount":   "^\$[0-9]+\.[0459]{2}",
    "Claim type":       "(AppleCare Plus)|(Worth Avenue Group)",
    "Description":      "Action Required",  # Get next array element
    "Notes":            "Tech’s Notes"  # All elements up to "Line Items"
}

# List of column headers from fields
headers = list(dict.fromkeys(searchStrings))

# List of fields which occasionally appear in the scope of other desired fields.
# Future exclusions can be added to this list
exceptionStrings = ["Warranty Start",
                    "6/18/2020",
                    "Warranty End",
                    "6/18/2023",
                    "Data Backup",
                    "Data Recovery",
                    "Computer User",
                    "Long Name",
                    "Line Items",
                    "6/17/2020",
                    "6/17/2023",
                    "Diagnostic Tests Performed"]


def getPdf():
    invoices = []
    FILE_PATH = filedialog.askopenfilenames()  # Get pdfs for conversion
    for i in range(len(FILE_PATH)):
        with open(FILE_PATH[i], "rb") as f:
            pdf = pdftotext.PDF(f)
        invoices.append(pdf)
    return invoices


def save():
    files = [('All Files', '*.*'),
             ('Python Files', '*.py'),
             ('Text Document', '*.txt')]
    file = asksaveasfile(filetypes=files, defaultextension=files)


def pdfToString(pdf):
    # Pages in the generated pdf
    # Array of PO numbers
    # Filtered values not matching search criteria
    pages, claims, trashVals = ([] for i in range(3))

    # Iterate through pdfs
    for i in range(len(pdf)):
        # Current pdf pages
        # Search matches
        dateCheck = False       # Boolean flag to filter superfluous date matches
        curPages, results = ([] for i in range(2))

        # Iterate through pages of current pdf
        for j in range(len(pdf[i])):
            # Convert current page of pdf to array
            stringList = [i for i in pdf[i][j].split('\n') if i]

            # Iterate through array
            for k in range(len(stringList)):
                for key in searchStrings:
                    serials = []
                    x = {}

                    # Serial number as container
                    if key == "Serial number":
                        sn = re.search(searchStrings[key], stringList[k])
                        try:
                            sn = sn.group(0)
                            serials.append(sn)
                        except AttributeError:
                            continue

                    # Group "Description" field elements
                    if key == "Description":
                        try:
                            if stringList[k].index(searchStrings[key]) is not None:
                                counter = k
                                firstTrigger = True
                                while stringList[counter+1] != "Diagnostic Tests Performed":
                                    counter = counter+1
                                    if stringList[counter] in exceptionStrings:
                                        continue
                                    elif re.search("^(Asset Tag:)", stringList[counter]) is not None:
                                        continue
                                    elif firstTrigger:
                                        x[key] = stringList[counter]
                                        firstTrigger = False
                                    else:
                                        x[key] = f"{x[key]}, {stringList[counter]}"
                            else:
                                x[key] = "No description provided"
                        except ValueError:
                            continue
                        except KeyError:
                            print(stringList)

                    # Group "Notes" field elements
                    elif key == "Notes":
                        try:
                            if stringList[k].index(searchStrings[key]) >= -1:
                                counter = k+1
                                while stringList[counter] not in exceptionStrings:
                                    if counter == k+1:
                                        x[key] = stringList[counter]
                                    else:
                                        x[key] = f"{x[key]}, {stringList[counter]}"
                                    counter = counter+1
                        except ValueError:
                            continue

                    # Ignore repeat dates
                    elif key == "Date" and dateCheck is True:
                        continue

                    # Find fields by regex search strings
                    else:
                        x[key] = re.search(searchStrings[key], stringList[k])

                    # Check that value is returned
                    try:
                        if x[key] is not None:
                            try:
                                x[key] = x[key].group(0)
                                if key == "Invoice" and x[key] not in claims:
                                    claims.append(x[key])
                                elif key == "Date":
                                    dateCheck = True
                                results.append(x)
                            except AttributeError:  # Add non regex-matched results
                                if x[key] != "None":
                                    results.append(x)
                                    continue
                                else:
                                    continue
                    except KeyError:
                        print(x)
                        # if x[key] != "None":
                        #     results.append(x)
                    else:
                        trashVals.append(stringList[k])

        # Compile search matches into array for page
        seen = set()
        page = []

        # Remove duplicates
        for d in results:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                page.append(d)
        # print(page)
        pages.append(page)
    trashVals = list(dict.fromkeys(trashVals))
    pages.insert(0, claims)
    for page in pages:
        for i in page:
            if 'Serial number' not in [*i]:
                print(page)

    # We don't like conflicts.  We don't like any breakfast cereals.
    conflicts = [x for x in trashVals if x in pages[2:]]
    print(f"Conflicts: {conflicts}")
    return pages


# Clean and fix anomalies
def prepareDataForColumns(df_index, rows):
    extraRows = []              # Rows to add after cleaning
    deleteIndex = []            # Index of extra elements to be deleted after being moved
    serials = []                # Serial numbers
    invoiceNos = {"No invoice no. found": []}             # Duplicates by invoice number

    # Clean up and remove superfluous dates
    for x in range(len(rows)):  # Debugging loop -- check for duplicate fields
        size = len(rows[x])
        innerDict = {}
        for key in searchStrings:
            countsOfKey = sum(1 for s in rows[x] if key in s)
            if countsOfKey == 0:
                try:
                    rows[x][key] = "No value found"
                except TypeError:
                    print(f"countsOfKey: {countsOfKey}")
            if countsOfKey >= 2:
                extraRows.append([dict(rows[x][i]) for i,
                                  item in enumerate(rows[x]) if key in item][1:])

                # Find duplicate index values from current row
                for y in extraRows:
                    i = len(y)-1
                    try:
                        while i >= 1:
                            deleteIndex.append(rows[x].index(y[i]))
                            i -= 1
                        innerDict[key] = list(list(a.values())[0] for a in y)
                    except ValueError:
                        print(
                            f"**************\n\nKey = {key}\n\nX = {rows[x]}\n\nExtras = {y}\n\ninnerDict = {innerDict}\n\ndeleteIndex = {deleteIndex}\n\n**************")
                try:
                    invoiceNos[rows[x][1]["Invoice"]] = innerDict
                except KeyError:
                    print(f"Keyerror X = {rows[x]}")

        # Items to delete like the ichorous pustules that they are
        poppers = list(dict.fromkeys(deleteIndex))
        poppers.sort(reverse=True)  # Reverse order to simplify deletion

        # Start deletion
        if size != len(searchStrings):
            for y in poppers:
                try:
                    rows[x].pop(y)
                except AttributeError:
                    break

        rowDict = {}
        for i in rows[x]:
            for k, v in i.items():
                rowDict.setdefault(k, v)
            rows[x] = rowDict

    # Associate extra rows with invoice # and add to main array
    tfExtras = np.array(extraRows).transpose()
    zRows = []
    for idx, x in enumerate(rows):
        for key in invoiceNos:
            try:
                if x['Invoice'] == key:
                    try:
                        for i in range(tfExtras.shape[0]):
                            tmp = dict(x)
                            for sKeys in invoiceNos[key]:
                                tmp[sKeys] = invoiceNos[key][sKeys][0]
                                invoiceNos[key][sKeys].pop(0)
                            zRows.append([idx+1, dict(tmp)])
                    except KeyError:
                        print(x['Invoice'])
            except KeyError:
                x['Invoice'] = key
    for i in zRows:
        df_index.insert(i[0], i[1]['Invoice'])
        rows.insert(i[0], i[1])

    # Return cleaned list
    return [df_index, rows]


# Replace row values
def replaceValues(x):
    print("nothing yet")


pdf = getPdf()
pages = pdfToString(pdf)
df_index = pages[0]
rows = pages[1:]
cleanRows = prepareDataForColumns(df_index, rows)

for i in cleanRows[1]:
    print(i)
# Convert to dataframe (future simplification)
df = pd.DataFrame(cleanRows[1], index=cleanRows[0])

df.to_csv(
    f"/Users/john.tamm-buckle/Documents/CompAVTech/computer solutions copy/csv/Invoices_{df_index[0]}_to_{df_index[-1]}_processed_{re.sub(r'/', '-', str(datetime.date.today()))}.csv")


# Read all the text into one string
# open("/Users/john.tamm-buckle/Documents/CompAVTech/computer solutions/2021-2022 invoices/08132021/testpdf.txt", "wt").write("\n\n".join(pdf))
