from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from KYCData.models import details

import os
import re
from PIL import Image
import pytesseract
import cv2
import numpy as np
from pytesseract import Output
import pytesseract
import sys
import ftfy


def image_to_kyc_data(request):
    if request.method == "POST":
        if request.POST.get("img"):
            new_file = request.FILES['document']
            fs = FileSystemStorage()
            our_file = fs.save(new_file.name, new_file)

            tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
            img = our_file
            # PAN TYPE-1

            def pan_read_data_type_1(text):
                name = ""
                fname = ""
                dob = ""
                pan = ""
                gender = ""
                nameline = []
                dobline = []
                panline = []
                text0 = []
                text1 = []
                text2 = []
                lines = text.split('\n')
                for lin in lines:
                    s = lin.strip()
                    s = lin.replace('\n', '')
                    s = s.rstrip()
                    s = s.lstrip()
                    text1.append(s)
                text1 = list(filter(None, text1))
                lineno = 0
                for wordline in text1:
                    xx = wordline.split('\n')
                    if ([w for w in xx if re.search('(INCOMETAXDEPARWENT|INCOME|TAX|GOW|GOVT|GOVERNMENT|OVERNMENT|VERNMENT|DEPARTMENT|EPARTMENT|PARTMENT|ARTMENT|INDIA|NDIA)$', w)]):
                        text1 = list(text1)
                        lineno = text1.index(wordline)
                        break
                text0 = text1[lineno+1:]
                try:
                    # Cleaning first names
                    name = text0[0]
                    name = name.rstrip()
                    name = name.lstrip()
                    name = name.replace("8", "B")
                    name = name.replace("0", "D")
                    name = name.replace("6", "G")
                    name = name.replace("1", "I")
                    name = re.sub('[^a-zA-Z] +', ' ', name)
            # Cleaning Father's name
                    fname = text0[1]
                    fname = fname.rstrip()
                    fname = fname.lstrip()
                    fname = fname.replace("8", "S")
                    fname = fname.replace("0", "O")
                    fname = fname.replace("6", "G")
                    fname = fname.replace("1", "I")
                    fname = fname.replace("\"", "A")
                    fname = re.sub('[^a-zA-Z] +', ' ', fname)
            # Cleaning DOB
                    DOB = re.search("\d{2}/\d{2}/\d{4}", text)
                    if DOB != None:
                        dob = DOB.group()
            # Cleaning PAN Card details'

                    text0 = findword(
                        text1, '(Pormanam|Number|umber|Account|ccount|count|Permanent|ermanent|manent|wumm)$')
                    panline = text0[0]
                    pan = panline.rstrip()
                    pan = pan.lstrip()
                    pan = pan.replace(" ", "")
                    pan = pan.replace("\"", "")
                    pan = pan.replace(";", "")
                    pan = pan.replace("%", "L")
                except:
                    pass
                data = {}
                data['Name'] = modify(name)
                data['FatherName'] = modify(fname)
                data['DateofBirth'] = dob
                data['idno'] = pan
                data['IDType'] = "PAN"
                data['gender'] = gender
                data['image'] = new_file.name
                return data

            # PAN TYPE-2
            def pan_read_data_type_2(str):
                name = ""
                fname = ""
                dob = ""
                pan = ""
                gender = ""
                count = 0
                DOB = re.search("\d{2}/\d{2}/\d{4}", str)
                if DOB != None:
                    dob = DOB.group()
                refined = str.split('\n')
                refined.remove('')
                for i in range(len(refined)):
                    if 'name' in refined[i].lower() and count == 0:
                        name += refined[i+1]
                        count += 1
                    if 'father' in refined[i].lower():
                        fname += refined[i+1]
                    if 'account' in refined[i].lower():
                        pan = refined[i+2]
                data = {}
                data['Name'] = modify(name)
                data['FatherName'] = modify(fname)
                data['DateofBirth'] = dob
                data['idno'] = pan
                data['IDType'] = "PAN"
                data['gender'] = gender
                data['image'] = new_file.name
                return data

            # Aadhar data
            def adhaar_read_data(text):
                res = text.split()
                name = None
                dob = None
                adh = None
                sex = None
                nameline = []
                dobline = []
                text0 = []
                text1 = []
                text2 = []
                lines = text.split('\n')
                for lin in lines:
                    s = lin.strip()
                    s = lin.replace('\n', '')
                    s = s.rstrip()
                    s = s.lstrip()
                    text1.append(s)

                if 'female' in text.lower():
                    sex = "FEMALE"
                else:
                    sex = "MALE"

                text1 = list(filter(None, text1))
                text0 = text1[:]

                try:
                    DOB = re.search("\d{2}/\d{2}/\d{4}", text)
                    if DOB != None:
                        dob = DOB.group()

                    splitted_text = text.split('\n')
                    for i in range(len(splitted_text)):
                        if dob in splitted_text[i]:
                            name = splitted_text[i-1]

                    # Cleaning Adhaar number details
                    aadhar_number = ''
                    for word in res:
                        if len(word) == 4 and word.isdigit():
                            aadhar_number = aadhar_number + word + ' '
                    if len(aadhar_number) >= 14:
                        print("Aadhar number is :" + aadhar_number)
                    else:
                        print("Aadhar number not read")
                    adh = aadhar_number

                except:
                    pass

                data = {}
                data['Name'] = modify(name)
                data['DateofBirth'] = dob
                data['idno'] = adh
                data['gender'] = sex
                data['fname'] = ""
                data['IDType'] = "Adhaar"
                data['image'] = new_file.name
                return data
            # Find word function

            def findword(textlist, wordstring):
                lineno = -1
                for wordline in textlist:
                    xx = wordline.split()
                    if ([w for w in xx if re.search(wordstring, w)]):
                        lineno = textlist.index(wordline)
                        textlist = textlist[lineno+1:]
                        return textlist
                return textlist

            # Modify names
            def modify(line):
                new_line = ""
                for i in line.split():
                    if len(i) >= 3:
                        new_line += i+" "
                return new_line

            # 1)Image Extraction
            filename = img
            img = cv2.imread(filename)

            # 2| Text Extraction using Tesseract and fixing the text
            pan_type = 1
            text = pytesseract.image_to_string(
                Image.open(filename), lang='eng')
            if "name" in text.lower() or "father" in text.lower() or "fath" in text.lower():
                pan_type = 2
            text = ftfy.fix_text(text)
            text = ftfy.fix_encoding(text)

            # 3| Check whether PAN or Aadhaar
            if "income" in text.lower() or "tax" in text.lower() or "department" in text.lower():
                if pan_type == 1:
                    data = pan_read_data_type_1(text)
                else:
                    data = pan_read_data_type_2(text)
            elif "male" in text.lower():
                data = adhaar_read_data(text)
            try:
                if data['IDType'] == "PAN":
                    return render(request, 'pan_data.html', data)
                else:
                    return render(request, 'aadhar_data.html', data)
            except:
                return render(request, 'error.html')
                pass
        elif request.POST.get("idtype"):
            name = request.POST.get('name')
            fname = request.POST.get('fname')
            idno = request.POST.get('idno')
            dob = request.POST.get('dob')
            idtype = request.POST.get('idtype')
            gender = request.POST.get('gender')
            info = details(name=name, fname=fname, id_no=idno,
                           dob=dob, id_type=idtype, gender=gender)
            info.save()
            # # To delete file
            # if os.path.isfile(our_file):
            #     os.remove(our_file)
            return render(request, 'image_to_kyc_data.html')
        else:
            return render(request, 'image_to_kyc_data.html')

    else:
        return render(request, 'image_to_kyc_data.html')
