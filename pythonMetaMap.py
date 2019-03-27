from pymetamap import MetaMap
import os
from xml.etree import cElementTree as etree
import re
import xml.dom.minidom
import sys
from termcolor import colored

obesity_cuis = ["C0028754"]
hypertension_cuis = ["C0020538"]
cad_cuis = ["C0018802"]

def run():
    mypath = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/training-RiskFactors-Complete-Set1"
    files = [f for f in os.listdir(mypath)]

    uda_path = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/"
    acronyms = ["CAD|coronary artery disease\n"]
    uda = open(uda_path + "UDA_custom.txt", 'w')
    for ac in acronyms:
        uda.write(ac)
    uda.close()

    os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(uda_path + "UDA_custom.txt", "UDA_custom_ascii.txt"))

    count = 0
    for x in files:
        filepath = mypath + "/" + x
        print(filepath)
        new_file = mypath + "/" + os.path.splitext(x)[0] + "_.xml"
        os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(filepath, new_file))

        tree = etree.parse(new_file)
        root = tree.iter()
        text = ""

        for i in root:
            if i.tag == "TEXT":
                text = i
                break
        mm = MetaMap.get_instance("/Users/josephconstant/Documents/University_of_Iowa/public_mm/bin/metamap16")
        sents = str(text.text).split("\n")
        for sentence in sents:
            if sentence == '' or sentence == ' ':
                sents.remove(sentence)
        # concepts, error = mm.extract_concepts(sents, conjunction_processing=False, negation_detection=True,
        #                                       blanklines=True, out_file_name="test-1_out.txt", UDA="{}UDA_custom_ascii.txt".format(uda_path),
        #                                       ExcludeSemTypes="gngm,elii,food,orgt")

        # concepts, error = mm.extract_concepts(sents, conjunction_processing=False, negation_detection=True,
        #                                       blanklines=True, out_file_name="test-1_out.txt",
        #                                       UDA=None, ExcludeSemTypes="gngm,elii,food,orgt")

        parseRawText(sents)

        #outputXML(text.text, new_file)

        # parseConcepts(concepts)
        if count > 99:
            break
        count += 1


def outputXML(text, file):
    doc = xml.dom.minidom.Document()
    article = doc.createElement('root')
    content = doc.createCDATASection('<![CDATA[\n{}]]>'.format(text))
    article.appendChild(content)
    findings = doc.createElement("TAGS")
    handle = open(file, 'w')
    article.writexml(handle)
    handle.close()
    print(file)


def parseConcepts(concepts):
    for concept in concepts:
        print(concept)


def parseRawText(text):
    obese = False
    hypertension = False
    hyperlipidemia = False

    for i in range(0,len(text)):
        if i < len(text)-1:
            line = text[i] + " " +  text[i + 1]
        else:
            line = text[i]
        obese = checkObesity(line, obese)
        hypertension = checkHypertension(line, hypertension)
        hyperlipidemia = checkCholesterol(line, hyperlipidemia)

    print("Obese: {} Hypertension: {} High Chol: {}".format(obese, hypertension, hyperlipidemia))


def checkObesity(line, obese):
    if "obese" in line.lower() and not obese:
        # print("Is obese")
        obese = True
    if "bmi" in line.lower() and not obese:
        x = re.search('bmi.*(?P<bmi>\s\d+\.\d*)', line.lower())
        if x:
            if float(x.group("bmi")) > 30.0:
                obese = True
    return obese


def checkHypertension(line, hypertension):
    if "htn" in line.lower() or "hypertension" in line.lower() and not hypertension:
        hypertension = True
    if "bp" in line.lower() or "blood pressure" in line.lower() and not hypertension:
        if "bp" in line.lower():
            y = re.search("bp.+(?P<systolic>\s\d+)/(?P<diastolic>\d+)", line.lower())
            if y:
                if int(y.group("systolic")) > 140 or int(y.group("diastolic")) > 90:
                    hypertension = True
        if "blood pressure" in line.lower():
            if "high blood pressure" in line.lower():
                hypertension = True
            y = re.search("blood pressure\D*(?P<systolic>\d+)/(?P<diastolic>\d+)", line.lower())
            if y:
                if int(y.group("systolic")) > 140 or int(y.group("diastolic")) > 90:
                    hypertension = True
    return hypertension


def checkCholesterol(line, hyperlipidemia):
    if "hyperlipidemia" in line.lower() or "hypercholesterolemia" in line.lower() or "high cholesterol" in line.lower() and not hyperlipidemia:
        hyperlipidemia = True

    if "CHOL" in line and not hyperlipidemia:
        # Needs to be lower. Ex. in 304-01.xml
        y = re.search("CHOL\D*(?P<total>\d+)", line)
        if y:
            print(colored(line, 'green'))
            # print("Cholesterol: {}".format(int(y.group("total"))))
            if int(y.group("total")) > 240:
                print(colored("Has high cholesterol", 'red'))
                hyperlipidemia = True

    if "cholesterol" in line.lower() and not hyperlipidemia:
        y = re.search("cholesterol\D+\d+/\d+/\d+\s+(?P<total>\d+)", line.lower())
        if y:
            print("Cholesterol: {}".format(int(y.group("total"))))
            if int(y.group("total")) > 240:
                print(colored("Has high cholesterol", 'red'))
                hyperlipidemia = True
            else:
                if "-ldl" in line.lower():
                    if int(y.group("total")) > 100:
                        print(colored("Has high-ldl", 'red'))
                        hyperlipidemia = True
        y = re.search("cholesterol\D*(?P<total>\d+)", line.lower())
        if y:
            print(colored(line, 'green'))
            # print("Cholesterol: {}".format(int(y.group("total"))))
            if int(y.group("total")) > 240:
                print(colored("Has high cholesterol", 'red'))
                hyperlipidemia = True

    if "ldl" in line.lower() and not hyperlipidemia:
        y = re.search("ldl\s\D*(?P<ldl>\d+)", line.lower())
        if y:
            print(colored(line, 'green'))
            if int(y.group("ldl")) > 100:
                print(colored("Has high ldl", 'red'))
                hyperlipidemia = True

    # Has not been seen in test data
    if "low density lipoprotein" in line.lower():
        print(colored(line, 'blue'))

    return hyperlipidemia


if __name__ == "__main__":
    MetaMapDir = "/Users/josephconstant/Documents/University_of_Iowa/public_mm/bin/"
    #os.system("{}skrmedpostctl start".format(MetaMapDir))
    #os.system("{}wsdserverctl start".format(MetaMapDir))
    run()
    #os.system("{}skrmedpostctl stop".format(MetaMapDir))
    #os.system("{}wsdserverctl stop".format(MetaMapDir))
