from pymetamap import MetaMap
import os
import xml.etree.ElementTree as ET
import xml
import re
import xml.dom.minidom
import sys
from termcolor import colored

obesity_cuis = ["C0028754"]
hypertension_cuis = ["C0020538"]
cad_cuis = ["C0018802"]
debug = False


def run(directory):
    if directory is None:
        directory = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/training-RiskFactors-Complete-Set1"
    files = [f for f in os.listdir(directory)]

    uda_path = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/"
    acronyms = ["CAD|coronary artery disease\n"]
    uda = open(uda_path + "UDA_custom.txt", 'w')
    for ac in acronyms:
        uda.write(ac)
    uda.close()

    # os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(uda_path + "UDA_custom.txt", "UDA_custom_ascii.txt"))

    count = 0
    for x in files:
        filepath = directory + "/" + x
        if debug:
            print(filepath)
        new_file = directory + "/" + os.path.splitext(x)[0] + "_.xml"
        os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(filepath, new_file))

        processFile(new_file)

        # mm = MetaMap.get_instance("/Users/josephconstant/Documents/University_of_Iowa/public_mm/bin/metamap16")
        # concepts, error = mm.extract_concepts(sents, conjunction_processing=False, negation_detection=True,
        #                                       blanklines=True, out_file_name="test-1_out.txt", UDA="{}UDA_custom_ascii.txt".format(uda_path),
        #                                       ExcludeSemTypes="gngm,elii,food,orgt")

        # concepts, error = mm.extract_concepts(sents, conjunction_processing=False, negation_detection=True,
        #                                       blanklines=True, out_file_name="test-1_out.txt",
        #                                       UDA=None, ExcludeSemTypes="gngm,elii,food,orgt")


def parseConcepts(concepts):
    for concept in concepts:
        print(concept)


def processFile(filename):
    tree = xml.etree.ElementTree.parse(filename)
    root = tree.iter()
    text = ""

    for i in root:
        if i.tag == "TEXT":
            text = i
            break

    sents = str(text.text).split("\n")
    for sentence in sents:
        if sentence == '' or sentence == ' ':
            sents.remove(sentence)

    tree = parseRawText(sents)
    if debug:
        tree.write("{}_out.xml".format(filename))
    return tree


def parseRawText(text):
    obese = False
    o_mention = False
    bmi = False
    waist = False
    hypertension = False
    h_mention = False
    bp = False
    hyperlipidemia = False
    c_mention = False
    total = False
    ldl = False

    for i in range(0,len(text)):
        if i < len(text)-1:
            line = text[i] + " " +  text[i + 1]
        else:
            line = text[i]
        if not obese:
            obese, o_mention, bmi, waist = checkObesity(line, obese, o_mention, bmi, waist)
        if not hypertension:
            hypertension, h_mention, bp = checkHypertension(line, hypertension, h_mention, bp)
        if not hyperlipidemia:
            hyperlipidemia, c_mention, total, ldl = checkCholesterol(line, hyperlipidemia, c_mention, total, ldl)

    positive_conditions = []
    if obese:
        if o_mention:
            positive_conditions.append(["OBESE", "mention"])
        elif bmi:
            positive_conditions.append(["OBESE", "BMI"])
        else:
            positive_conditions.append(["OBESE", "waist"])
    if hypertension:
        if h_mention:
            positive_conditions.append(["HYPERTENSION", "mention"])
        else:
            positive_conditions.append(["HYPERTENSION", "high bp"])
    if hyperlipidemia:
        if c_mention:
            positive_conditions.append(["HYPERLIPIDEMIA", "mention"])
        if total:
            positive_conditions.append(["HYPERLIPIDEMIA", "high cholesterol"])
        if ldl:
            positive_conditions.append(["HYPERLIPIDEMIA", "high LDL"])

    if debug:
        print("Obese: {} Hypertension: {} High Chol: {}".format(obese, hypertension, hyperlipidemia))
        print(positive_conditions)

    return outputXML(positive_conditions)


def checkObesity(line, obese, mention, bmi, waist):
    lower = line.lower()
    if "obese" in lower and not obese:
        # print("Is obese")
        obese = True
        mention = True
    if "bmi" in lower and not obese:
        x = re.search('bmi.*(?P<bmi>\s\d+\.\d*)', lower)
        if x:
            if float(x.group("bmi")) > 30.0:
                obese = True
                bmi = True
    return obese, mention, bmi, waist


def checkHypertension(line, hypertension, mention, high_bp):
    lower = line.lower()
    if "htn" in lower or "hypertension" in lower or "high bp" in lower and not hypertension:
        hypertension = True
        mention = True
    if "bp" in lower or "blood pressure" in lower and not hypertension:
        if "bp" in lower:
            y = re.search("bp.+(?P<systolic>\s\d+)/(?P<diastolic>\d+)", line.lower())
            if y:
                if int(y.group("systolic")) > 140 or int(y.group("diastolic")) > 90:
                    hypertension = True
                    high_bp = True
        if "blood pressure" in lower:
            if "high blood pressure" in lower:
                hypertension = True
                mention = True
            elif "elevated blood pressure" in lower:
                hypertension = True
                mention = True
            else:
                y = re.search("blood pressure\D*(?P<systolic>\d+)/(?P<diastolic>\d+)", line.lower())
                if y:
                    if int(y.group("systolic")) > 140 or int(y.group("diastolic")) > 90:
                        hypertension = True
                        high_bp = True
    return hypertension, mention, high_bp


def checkCholesterol(line, hyperlipidemia, mention, total, ldl):
    lower = line.lower()
    if "hyperlipidemia" in lower or "hypercholesterolemia" in lower or "high cholesterol" in lower and not hyperlipidemia:
        hyperlipidemia = True
        mention = True
    elif "dyslipidemia" in lower or "elevated cholesterol" in lower or "high chol" in lower and not hyperlipidemia:
        hyperlipidemia = True
        mention = True
    elif "high ldl" in lower and not hyperlipidemia:
        hyperlipidemia = True
        mention = True

    if "CHOL" in line and not hyperlipidemia:
        y = re.search("CHOL\D*(?P<total>\d+)", line)
        if y:
            if int(y.group("total")) > 240:
                hyperlipidemia = True
                total = True

    if "cholesterol" in lower and not hyperlipidemia:
        y = re.search("cholesterol\D+\d+/\d+/\d+\s+(?P<total>\d+)", lower)
        if y:
            if int(y.group("total")) > 240:
                hyperlipidemia = True
                total = True
                print(colored("High total cholesterol", 'red'))
                print(lower)
            else:
                if "-ldl" in lower:
                    if int(y.group("total")) > 100:
                        print(colored("High LDL cholesterol", 'green'))
                        print(colored(lower, 'green'))
                        hyperlipidemia = True
                        ldl = True
        y = re.search("cholesterol\D*(?P<total>\d+)", lower)
        if y:
            if int(y.group("total")) > 240:
                hyperlipidemia = True
                total = True
                print(colored("High total cholesterol", 'red'))
                print(lower)

    if "ldl" in line.lower() and not hyperlipidemia:
        y = re.search("ldl\s\D*(?P<ldl>\d+)", line.lower())
        if y:
            if int(y.group("ldl")) > 100:
                hyperlipidemia = True
                ldl = True
                print(colored("High LDL cholesterol", 'green'))
                print(colored(lower, 'green'))

    # Has not been seen in test data
    if "low density lipoprotein" in line.lower():
        print(colored(line, 'blue'))

    return hyperlipidemia, mention, total, ldl


def outputXML(conditions):
    root = ET.Element('root')
    tags = ET.Element('TAGS')
    for x in conditions:
        tag = x[0]
        indicator = x[1]
        if debug:
            # Debug statement
            print("Debug")
        print("Tag: {} Indicator: {}".format(tag, indicator))
        if tag.lower() == "obese":
            elem = ET.Element('OBESE', attrib={'indicator': indicator, 'time': 'before DCT'})
            tags.insert(1, elem)
        if tag.lower() == "hypertension":
            elem = ET.Element('HYPERTENSION', attrib={'indicator': indicator, 'time': 'before DCT'})
            tags.insert(1, elem)
        if tag.lower() == "hyperlipidemia":
            elem = ET.Element('HYPERLIPIDEMIA', attrib={'indicator': indicator, 'time': 'before DCT'})
            tags.insert(1, elem)
    root.append(tags)
    tree = ET.ElementTree(root)

    return tree


if __name__ == "__main__":
    run(None)
    # MetaMapDir = "/Users/josephconstant/Documents/University_of_Iowa/public_mm/bin/"
    # os.system("{}skrmedpostctl start".format(MetaMapDir))
    # os.system("{}wsdserverctl start".format(MetaMapDir))
    # os.system("{}skrmedpostctl stop".format(MetaMapDir))
    # os.system("{}wsdserverctl stop".format(MetaMapDir))
