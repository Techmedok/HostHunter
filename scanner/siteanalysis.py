from groq import Groq
import re
import json

def extract_json(text):
    pattern = r'```json(.*?)```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return json.loads(match.group(1).strip())
    else:
        return None

def SiteAnalysis(content):
    client = Groq(api_key="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")
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[        {
                "role": "user",
                "content": f"""
                                I need the following data in JSON format:
                                    summary (Paragraphs appended in String),
                                    keywords (array),
                                    site category (String)
                                I dont need any other data other than this in your output.
                                Site Contents:
                                {content}
                            """,
            }],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,
        stop=None,
    )

    return extract_json(completion.choices[0].message.content)


content="""


    Smart India Hackathon Login/Register

    Home(current)
    About SIH
    Guidelines
    Problem Statements
    Know Your SPOC
    Project Implementation
    FAQs
    Contact us

Slide One
Click here to see the Wildcard teams of sih 2024  SIH Repository for Team Standee, Tshirts and Banners  Request Letter to All Head of Institutes from Chairman, AICTE regarding rescheduling of End Term/Semester Exams  Click here to see the screening result for sih 2024 
Shortlisted teams of SIH 2024
View
Letter for Rescheduling Exam
View
Nodal Center List for SIH 2024
View
Login for Smart India Hackathon 2024
SIH Login/Register
WHAT IS SIH?

Smart India Hackathon (SIH) is a premier nationwide initiative designed to engage students in solving some of the most pressing challenges faced in everyday life. Launched to foster a culture of innovation and practical problem-solving, SIH provides a dynamic platform for students to develop and showcase their creative solutions to real-world problems. By encouraging participants to think critically and innovatively, the hackathon aims to bridge the gap between academic knowledge and practical application.

Since its inception, SIH has garnered significant success in promoting out-of-the-box thinking among young minds, particularly engineering students from across India. Each edition has built on the previous one, refining its approach and expanding its impact. The hackathon not only offers students an opportunity to showcase their skills but also encourages collaboration with industry experts, government agencies, and other stakeholders.
image
THEMES
No problem is too big... No idea is too small
SIH process flow and Timeline
image
Why SIH is important for Government department and Corporate department
Innovative Solutions

Get innovative solutions to your problems in cost effective ways Opportunity to be a part of Nation Building Opportunity to brand your company.
Recognition and visibility

Nationally Recognition and visibility for your company across all premier institutions in India
Out-of-the-box solutions

Talented youngsters from all over the country offer out-of-the-box solutions to your problems
Innovation Movement Opportunity

Be part of World’s biggest Open Innovation Movement Opportunity to work with some of the best talents in the country
SIH Milestones
8,98,884

Participating Students
6000+

SIH Alumni Network
3897

Participating Institutes
2633

Total Problem Statements
100+

Registered Startups

    Organizing Committee Executive Committee 

Patron
Shri Narendra Modi

Hon'ble Prime Minister of India
Shri Dharmendra Pradhan

Hon'ble Minister of Education
Co-Patrons
Dr. Sukanta Majumdar

Hon'ble Minister of State for Education
Jayant Chaudhary

Hon'ble Minister of State for Education
Shri K. Sanjay Murthy

Hon'ble Secretary, Higher Education
Prof. T. G. Sitharam

Chairman, AICTE
Dr. Abhay Jere

Vice Chairman, AICTE
Organisers
logo logo logo logo

Official Partner

    image

Evaluation Partner

    image

Official Media Partner

    image image 

Learning Partner

    image

Platform Partner

    image 

Follow Us

© 2024-25 Smart India Hackathon. All rights reserved
Contact Us

    +91 11 29581241, +91 11 29581240
    sih@aicte-india.org,  hackathon@aicte-india.org


"""

out = SiteAnalysis(content)
print(out)
print(type(out))
