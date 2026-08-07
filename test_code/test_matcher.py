from matcher import match_skills

resume = {
    "python",
    "sql",
    "docker",
    "git",
    "tensorflow"
}

jd = {
    "python",
    "docker",
    "aws",
    "tensorflow"
}

result = match_skills(resume, jd)

print(result)