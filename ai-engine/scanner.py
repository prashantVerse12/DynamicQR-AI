import tldextract


danger_words = [
    "login",
    "verify",
    "password",
    "bank",
    "free",
    "gift",
    "crypto",
    "wallet"
]


def scan_url(url):

    score = 0

    reasons = []


    domain = tldextract.extract(url).domain


    if not url.startswith("https://"):

        score += 30

        reasons.append(
            "No HTTPS detected"
        )


    for word in danger_words:

        if word in url.lower():

            score += 15

            reasons.append(
                f"Suspicious keyword {word}"
            )


    if len(url) > 80:

        score += 20

        reasons.append(
            "URL too long"
        )


    if score < 30:

        status = "SAFE 🟢"

    elif score < 60:

        status = "SUSPICIOUS 🟡"

    else:

        status = "DANGEROUS 🔴"


    return {

        "domain": domain,

        "risk_score": score,

        "status": status,

        "reasons": reasons

    }