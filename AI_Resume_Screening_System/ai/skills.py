SKILLS = [

    "Python",

    "Java",

    "C",

    "C++",

    "HTML",

    "CSS",

    "JavaScript",

    "React",

    "Angular",

    "Node.js",

    "Flask",

    "Django",

    "SQL",

    "MongoDB",

    "Machine Learning",

    "Deep Learning",

    "TensorFlow",

    "Pandas",

    "NumPy"

]

def extract_skills(text):

    found = []

    text = text.lower()

    for skill in SKILLS:

        if skill.lower() in text:

            found.append(skill)

    return found