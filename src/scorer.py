def calculate_score(match_result:dict):
    #so the entire output of the matcher is passed into this function with some weights assigned to them
    score=match_result["skills"]["match_percentage"]*0.8 + match_result["experience"]["match"]*0.2
    
    return score