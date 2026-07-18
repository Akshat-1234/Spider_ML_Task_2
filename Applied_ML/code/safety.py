import re

#Checking whether the question is safe to answer

def safety_check(question):

    question = question.lower()

    emergency_words = [
        "heart attack",
        "having a stroke",
        "think i'm having a stroke",
        "unconscious",
        "can't breathe",
        "cant breathe",
        "cannot breathe",
        "not able to breathe",
        "difficulty breathing",
        "trouble breathing",
        "seizure",
        "overdose",
        "poison",
        "poisoned",
        "bleeding heavily",
        "severe bleeding",
        "chest pain"
    ]

    self_harm_words = [
        "suicide",
        "suicidal",
        "kill myself",
        "want to die",
        "end my life",
        "self harm",
        "hurting myself"
    ]

    diagnosis_words = [
        "diagnose",
        "diagnosis",
        "do i have",
        "do you think i have",
        "what disease do i have",
        "what illness do i have",
        "what is wrong with me",
        "am i sick with"
    ]

    prescription_words = [
        "prescribe",
        "prescription",
        "dosage",
        "dose",
        "how many mg",
        "how much should i take",
        "medicine should i take",
        "drug should i take",
        "antibiotic",
        "insulin dose"
    ]

    #Matching whole phrases only, not substrings

    def contains_phrase(text,phrase):
        pattern = r"\b" + re.escape(phrase) + r"\b"
        return re.search(pattern,text) is not None

    for word in self_harm_words:
        if contains_phrase(question,word):
            return (
                False,
                "It sounds like you might be going through something really difficult. "
                "Please reach out to a crisis line or emergency services in your area right now, "
                "or talk to someone you trust. You are not alone in this."
            )

    for word in emergency_words:
        if contains_phrase(question,word):
            return (
                False,
                "This appears to describe a medical emergency. Please contact your local emergency services or seek immediate medical attention."
            )

    for word in diagnosis_words:
        if contains_phrase(question,word):
            return (
                False,
                "I cannot diagnose medical conditions. Please consult a qualified healthcare professional."
            )

    for word in prescription_words:
        if contains_phrase(question,word):
            return (
                False,
                "I cannot recommend prescriptions or medication dosages. Please consult a licensed healthcare professional."
            )

    return True,""