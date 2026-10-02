

#the matcher function which uses & operation to find the skills the student has according to the jd
def match_skills(resume_skills: set[str], jd_skills: set[str]) -> dict:
    # Convert everything into lower case before comparing
    resume_skills = {s.strip().lower() for s in resume_skills if s.strip()}
    jd_skills = {s.strip().lower() for s in jd_skills if s.strip()}

    matched = resume_skills & jd_skills
    missing = jd_skills - resume_skills

    matched_percentage = (len(matched) / len(jd_skills)) * 100 if jd_skills else 100.0
    #either we can return it like matched,missing or like the dict form(recommended)
    return {
        "matched": matched,
        "missing": missing,
        "match_percentage": matched_percentage,
    }
    
 
 #experience matching function   
def match_experience(resume_exp: int | None, minimum_exp: int) -> dict:
    """
    Compare candidate experience with the minimum experience required.

    Args:
        resume_exp: Years of experience extracted from the resume.
        minimum_exp: Minimum years of experience required by the JD.

    Returns:
        A dictionary containing the comparison result.
    """

    if resume_exp is None:
        return {
            "matched": False,
            "candidate_experience": None,
            "required_experience": minimum_exp,
            "message": "Experience could not be extracted from the resume."
        }

    return {
        "matched": resume_exp >= minimum_exp,
        "candidate_experience": resume_exp,
        "required_experience": minimum_exp,
        "message": (
            "Experience requirement satisfied."
            if resume_exp >= minimum_exp
            else "Candidate does not meet the minimum experience requirement."
        )
    }
    
    
#this is the main function which basically uses the above the helper functions to compare the resume and the jd

def match_resume(resume, jd):
    resume_skills = set(resume.skills) if isinstance(resume.skills, (list, set)) else set()
    jd_skills = set(jd.skills) if hasattr(jd, "skills") and isinstance(jd.skills, (list, set)) else set()
    skills_result = match_skills(resume_skills, jd_skills)
    jd_exp = getattr(jd, "experience", getattr(jd, "minimum_experience", 0))
    exp_result = match_experience(resume.experience, jd_exp)
    
    return {
        "skills": skills_result,
        "experience": exp_result
    }