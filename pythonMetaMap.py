from pymetamap import MetaMap
import os
from xml.etree import cElementTree as ET
import tempfile
import re

obesity_cuis = ["C0028754"]
hypertension_cuis = ["C0020538"]
cad_cuis = ["C0018802"]

def run():
    mypath = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/training-RiskFactors-Complete-Set1"
    files = [f for f in os.listdir(mypath)]
    dirs = os.listdir(mypath)
    # print(dirs)

    # cat file | java -jar replace_utf8.jar > result

    uda_path = "/Users/josephconstant/Documents/University_of_Iowa/Health_Data_Analytics/Project_2/"
    acronyms = ["CAD|coronary artery disease\n"]
    uda = open(uda_path + "UDA_custom.txt", 'w')
    for ac in acronyms:
        uda.write(ac)
    uda.close()

    os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(uda_path + "UDA_custom.txt", "UDA_custom_ascii.txt"))

    for x in files:
        filepath = mypath + "/" + x
        print(filepath)
        # f = open(filepath, "r")
        # contents = f.readlines()
        new_file = mypath + "/" + os.path.splitext(x)[0] + "_.xml"
        os.system("cat {} | java -jar /usr/bin/replace_utf8.jar > {}".format(filepath, new_file))

        tree = ET.parse(new_file)
        root = tree.iter()
        text = ""

        for i in root:
            # print(i.tag)
            if i.tag == "TEXT":
                text = i
                break
        # for child in root:
        #     #print(child.tag, child.attrib)
        #     p = tree.find("TEXT")
        #     links = iter(p.iter("a"))
        #     for y in links:
        #         print(y)
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

        # for concept in concepts:
        #     print(concept)
        # parseConcepts(concepts)
        break


def parseConcepts(concepts):
    for concept in concepts:
        print(concept)

def parseRawText(text):
    is_obese = False
    has_htn = False
    has_cad = False
    for i in range(0,len(text)):
        if "HTN" in x and not has_htn:
            print("Has Hypertension")
            has_htn = True
        if "CAD" in x and not has_cad:
            if "no CAD" not in x:
                print("Has Coronary Artery Disease")
                has_cad = True
        if ("obese" or "Obese") in x and not is_obese:
            print("Is obese")
            is_obese = True
        if "BP" in x and not has_htn:
            y = re.search('BP\s(?P<systolic>\d+)/(?P<diastolic>\d+)', x)
            print("Blood Pressure: " + y.group("systolic") + "/" + y.group("diastolic"))
            if int(y.group("systolic")) > 140 or int(y.group("diastolic")) > 90:
                print("Has hypertension")
                has_htn = True






def markObesity():
    # do something
    print("Obesity")


if __name__ == "__main__":
    MetaMapDir = "/Users/josephconstant/Documents/University_of_Iowa/public_mm/bin/"
    os.system("{}skrmedpostctl start".format(MetaMapDir))
    os.system("{}wsdserverctl start".format(MetaMapDir))
    run()
    os.system("{}skrmedpostctl stop".format(MetaMapDir))
    os.system("{}wsdserverctl stop".format(MetaMapDir))
