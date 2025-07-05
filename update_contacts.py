import json

file_path = "/Users/admin/Desktop/Edu Guide/data/data.json"

new_contact_data = {
    "Build Bright University": {
        "phones": ["023 987 700", "012 682 777"],
        "website": "bbu.edu.kh"
    },
    "University of South-East Asia": {
        "phones": ["063 900 090"],
        "website": "usea.edu.kh"
    },
    "Cambodian University for Specialties": {
        "phones": ["012 636 207"],
        "website": "cus.edu.kh"
    },
    "Paññāsāstra University of Cambodia": {
        "phones": ["023 990 153", "087 866 363", "099 866 363"],
        "website": "puc.edu.kh"
    },
    "Angkor University": {
        "phones": ["017 671 825", "070 853 537"],
        "website": "angkor.edu.kh"
    },
    "Vanda Institute": {
        "phones": ["023 213 563"],
        "website": "vanda.edu.kh"
    },
    "National University of Battambang": {
        "phones": ["053 952 905", "010 711 866", "012 711 866"],
        "website": "https://nubb.edu.kh/en/"
    },
    "University of Management and Economics": {
        "phones": ["093 868 386", "012 473 768", "090 8888 32"],
        "website": "ume.edu.kh"
    },
    "Royal University of Phnom Penh": {
        "phones": ["023 883 640"],
        "website": "rupp.edu.kh"
    },
    "Institute of Technology of Cambodia": {
        "phones": ["023 880 370"],
        "website": "itc.edu.kh"
    },
    "Royal University of Agriculture": {
        "phones": ["011 967 877", "017 625 784"],
        "website": "rua.edu.kh"
    },
    "Royal University of Law and Economics": {
        "phones": ["012 88 36 85"],
        "website": "rule.edu.kh"
    },
    "Royal University of Fine Arts": {
        "phones": ["011 815 649"],
        "website": "rufa.edu.kh"
    },
    "University of Puthisastra": {
        "phones": ["023 221 624"],
        "website": "puthisastra.edu.kh"
    },
    "International University": {
        "phones": ["017 48 48 09", "016 423 666"],
        "website": "iu.edu.kh"
    },
    "National University of Management": {
        "phones": ["095 504 179"],
        "website": "https://numer.digital/"
    },
    "National Polytechnic Institute of Cambodia": {
        "phones": ["011769 003", "087506 680"],
        "website": "npic.edu.kh"
    },
    "Norton University": {
        "phones": ["093 888 569", "093 888 359"],
        "website": "norton-u.com"
    },
    "Royal Academy of Cambodia": {
        "phones": ["023 362 889"],
        "website": "rac.gov.kh"
    },
    "Royal School of Administration": {
        "phones": ["076 776 8888"],
        "website": "era.gov.kh"
    },
    "Cambodian Agricultural Research and Development Institute": {
        "phones": ["023 631 934"],
        "website": "cardi.org.kh"
    },
    "National Technical Training Institute": {
        "phones": ["023 883 039"],
        "website": "ntti.edu.kh"
    },
    "Prek Leap National College of Agriculture": {
        "phones": ["016 969 665"],
        "website": "nia.edu.kh"
    },
    "National University of Chea Sim Kamchaymear": {
        "phones": ["097 828 1168"],
        "website": "https://nuck.edu.kh/"
    },
    "National Institute of Business": {
        "phones": ["012 606 572", "012 853 030", "011 722 188"],
        "website": "nib.edu.kh"
    },
    "Preah Kosomak Polytechnic Institute": {
        "phones": ["012 766 488"],
        "website": "ppiedu.com"
    },
    "Cambodia Academy of Digital Technology": {
        "phones": ["015 335 877"],
        "website": "cadt.edu.kh"
    },
    "American University of Phnom Penh": {
        "phones": ["023 990 023"],
        "website": "https://www.aupp.edu.kh/"
    },
    "Phnom Penh International University": {
        "phones": ["023 999 908"],
        "website": "ppiu.edu.kh"
    },
    "Beltei International University": {
        "phones": ["078 555 507"],
        "website": "https://www.beltei.edu.kh/biu"
    },
    "Economics and Finance Institute": {
        "phones": ["023 885 855"],
        "website": "efi.mef.gov.kh"
    },
    "University of Cambodia": {
        "phones": ["023 993 276"],
        "website": "uc.edu.kh"
    },
    "Asia Europe University": {
        "phones": ["089 292 168", "098 292 168", "090 292 168"],
        "website": "aeu.edu.kh"
    },
    "Khemarak University": {
        "phones": ["012 49 33 34", "081 49 33 34", "097 707 1111"],
        "website": "https://khemarakuniversity.edu.kh/en"
    },
    "Human Resources University": {
        "phones": ["069 920 092"],
        "website": "hru.edu.kh"
    },
    "Chenla University": {
        "phones": ["012 535 080"],
        "website": "https://clu-edu.com/"
    },
    "Limkokwing University of Creative Technology": {
        "phones": ["015 582 801"],
        "website": "limkokwing.net/cambodia"
    },
    "Panha Chiet University": {
        "phones": ["016 667 698"],
        "website": "https://www.pcu.edu.kh/"
    },
    "Cambodia-Japan Cooperation Center": {
        "phones": ["023 883 649"],
        "website": "https://www.cjcc.edu.kh/en/"
    },
    "University of Economics and Finance": {
        "phones": ["010 516 887"],
        "website": "https://uef.edu.kh/academics/"
    },
    "National Institute of Public Health": {
        "phones": ["023 966 449"],
        "website": "niphr.edu.kh"
    },
    "National University of Social Affairs": {
        "phones": ["089 344 309", "012 462 911", "070 406 049"],
        "website": "nisa-edu.gov.kh"
    },
    "Western University": {
        "phones": ["096 8000 111"],
        "website": "https://westernuniversity.edu.kh/"
    }
}

with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

for university in data:
    if university["name_en"] in new_contact_data:
        university["contact"]["phones"] = new_contact_data[university["name_en"]]["phones"]
        university["contact"]["website"] = new_contact_data[university["name_en"]]["website"]

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
print("University contact information updated successfully.")
