RISK_CONFIG = {
    "termination": {
        "high": ["immediate termination", "without notice", "breach", "penalty", "liable"],
        "medium": ["30 days notice", "written notice", "obligation"],
        "low": ["mutual agreement", "expiry", "review"]
    },
    "indemnification": {
        "high": ["unlimited liability", "indemnify", "damages", "losses", "third party claim"],
        "medium": ["limited liability", "compensation", "reimburse"],
        "low": ["notify", "inform", "request"]
    },
    "confidentiality": {
        "high": ["perpetual", "strict confidentiality", "trade secret", "breach of confidentiality"],
        "medium": ["non disclosure", "restricted", "proprietary"],
        "low": ["general confidentiality", "inform", "review"]
    },
    "payment": {
        "high": ["default", "late penalty", "interest", "overdue", "forfeit"],
        "medium": ["invoice", "30 days payment", "installment"],
        "low": ["receipt", "acknowledge", "standard payment"]
    }
}

DEFAULT_RISK = {
    "high": ["terminate", "penalty", "liable", "breach", "damages", "indemnify", "forfeit"],
    "medium": ["obligation", "warranty", "comply", "restrict", "compensate"],
    "low": ["notice", "inform", "request", "review", "acknowledge"]
}

RISK_PRIORITY = {"high": 3, "medium": 2, "low": 1}