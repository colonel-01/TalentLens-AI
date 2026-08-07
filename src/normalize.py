SKILL_ALIASES = {
    "py": "python",
    "python3": "python",

    "ml": "machine learning",
    "machine-learning": "machine learning",

    "cpp": "c++",
    "c plus plus": "c++",

    "js": "javascript",

    "node": "node.js",
}

#this function normalises a single word
def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()

    if skill in SKILL_ALIASES:
        return SKILL_ALIASES[skill]

    return skill



#now this function take a list of skills as input and then applies the above funtion one by one and stores the result 
from typing import List


def normalize_skills(skills:List[str])-> List[str]:
    normalized=[]
    for skill in skills:
        normalized.append(normalize_skill(skill))
        
    return set(normalized) #set because it stores unique skills (not the repeated ones)


