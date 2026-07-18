import math

#Calculating confidence using reranker scores

def calculate_confidence(scores,sources):

    if len(scores)==0:
        return "Low",0

    #Converting raw logits to probabilities

    probs = [1/(1+math.exp(-s)) for s in scores]

    top_score = probs[0]
    second_score = probs[1] if len(probs)>1 else probs[0]

    average = sum(probs[:3])/min(3,len(probs))

    confidence = 40 + average*40 + (top_score-second_score)*20

    if any(source["source"]=="WHO" for source in sources):
        confidence += 8

    confidence = max(0,min(100,confidence))

    if confidence>=75:
        level="High"

    elif confidence>=55:
        level="Medium"

    else:
        level="Low"

    return level,round(confidence,2)
