import re
from typing import Optional

# Comprehensive football domain vocabulary (general football terms, tactics, rules, tournaments, awards, clubs, legends, football metrics)
FOOTBALL_KEYWORDS = {
    # Core & Match terms
    "football", "soccer", "futbol", "fútbol", "futebol",
    "match", "matches", "game", "games", "fixture", "fixtures", "derby", "derbies",
    "goal", "goals", "scorer", "scorers", "scoring", "scored", "scoreline", "score", "scores",
    "penalty", "penalties", "shootout", "freekick", "free-kick", "free kick", "corner", "corners",
    "foul", "fouls", "offside", "offsides", "handball", "red card", "yellow card", "card", "cards",
    "referee", "ref", "var", "pitch", "stadium", "bench", "substitute", "subs", "substitution",
    "half time", "halftime", "extra time", "stoppage time", "injury time", "clean sheet", "clean sheets",
    "hat-trick", "hattrick", "own goal", "xg", "expected goals", "assist", "assists", "pass", "passes",
    "tackle", "tackles", "dribble", "dribbles", "cross", "crosses", "header", "headers", "save", "saves",
    "lineup", "roster", "squad", "starting 11", "starting xi", "captain", "armband",
    "trophy", "trophies", "champion", "champions", "cup", "tournament", "league", "standings",
    "playoff", "playoffs", "relegation", "promotion", "relegated", "promoted", "title race",

    # Positions & Tactical Concepts
    "goalkeeper", "keeper", "gk", "defender", "defenders", "center-back", "cb", "full-back", "wing-back",
    "midfielder", "midfielders", "cm", "cdm", "cam", "winger", "wingers", "striker", "strikers", "forward", "forwards",
    "manager", "coach", "coaching", "tactical", "tactics", "formation", "formations",
    "false nine", "false 9", "gegenpress", "gegenpressing", "low block", "high line", "tiki-taka",
    "counter-attack", "counterattack", "park the bus", "zonal marking", "man marking", "possession",
    "transfer", "transfers", "transfer window", "loan", "contract", "signing", "release clause",

    # Football Mathematics, Contextual Metrics & Stats
    "win rate", "win percentage", "scoring rate", "goal difference", "goals per game", "goals per match",
    "shots per game", "shots per match", "shot", "shots", "possession percentage", "points",
    "team", "teams", "player", "players", "club", "clubs",

    # Competitions & Awards
    "world cup", "champions league", "ucl", "europa league", "euro", "euros", "copa america",
    "afcon", "premier league", "epl", "la liga", "serie a", "bundesliga", "ligue 1", "mls",
    "saudi pro league", "ballon d'or", "ballon dor", "golden boot", "golden glove", "fifa", "uefa", "conmebol",

    # Slang & Common Football Queries
    "goat", "el clasico", "el clásico", "north london derby", "top 4", "golden goal", "aggregate", "away goals", "underdog",

    # Well-known Clubs & National Teams
    "arsenal", "chelsea", "barcelona", "real madrid", "liverpool", "manchester city", "man city",
    "manchester united", "man utd", "tottenham", "spurs", "bayern", "dortmund", "psg", "juventus",
    "milan", "inter", "napoli", "roma", "atletico", "sevilla", "ajax", "benfica", "sporting", "boca",
    "river", "brazil", "argentina", "france", "england", "germany", "spain", "italy", "portugal",
    "netherlands", "holland", "belgium", "croatia", "morocco", "japan", "senegal",

    # Legends, Players & Managers
    "messi", "ronaldo", "pelé", "pele", "maradona", "cruyff", "zidane", "mbappe", "mbappé", "haaland",
    "bellingham", "vinicius", "neymar", "lewandowski", "kane", "saka", "palmer", "de bruyne",
    "guardiola", "klopp", "ancelotti", "ferguson", "mourinho", "arteta", "ten hag"
}

# Formation regex (e.g. 4-3-3, 4-2-3-1, 3-5-2, 4-4-2)
FORMATION_PATTERN = re.compile(r'\b\d-\d-\d(?:-\d)?\b')

# Standalone Pure Mathematics Patterns (unrelated to football)
MATH_PATTERNS = [
    # Explicit arithmetic with operations between numbers: e.g. "10 + 20", "50 * 3", "100 / 4", "2^3", "12345 / 67"
    re.compile(r'\b\d+(\.\d+)?\s*[\+\-\*/\^]\s*\d+(\.\d+)?\b'),
    
    # Word arithmetic: e.g. "12345 divided by 67", "100 divided by 4", "10 plus 20", "50 times 3", "80 minus 15"
    re.compile(r'\b\d+(\.\d+)?\s+(divided by|times|plus|minus|multiplied by)\s+\d+(\.\d+)?\b', re.I),
    
    # Standalone percentages of raw numbers: e.g. "25% of 400", "15% of 800", "25 percent of 400"
    re.compile(r'\b\d+(\.\d+)?\s*(%|percent)\s+of\s+\d+(\.\d+)?\b', re.I),
    
    # Algebra / Equations: e.g. "Solve x^2 + 5x + 6 = 0", "Solve 2x + 5 = 15", "Solve this equation", "x^2 + 3x + 2 = 0"
    re.compile(r'\b(solve|equation|equations|formula)\b', re.I),
    re.compile(r'\b[a-z]\s*[\^²³]\s*\d+|\b\d*[a-z]\s*[\+\-\*/=]\s*\d+', re.I),
    re.compile(r'\b\d+\s*=\s*\d+\b'),
    
    # Calculus & Higher Math: e.g. "derivative of x^2", "integrate x^2", "square root of 144", "sqrt(144)"
    re.compile(r'\b(derivative|derivatives|integrate|integration|integral|integrals|antiderivative|calculus|algebra|trigonometry|matrix|matrices|logarithm|log|sine|cosine|tangent|square root|sqrt|pythagorean)\b', re.I),
    
    # Pure mathematical operations on abstract numbers: e.g. "Calculate the average of 10, 20, and 30", "What is the sum of 5 and 10"
    re.compile(r'\b(average|sum|product|mean|median|mode|std dev|standard deviation)\s+of\s+(\d+|[a-z]\b)', re.I),
    re.compile(r'\bwhat\s+is\s+\d+(\.\d+)?\s*[\+\-\*/\^]\s*\d+\b', re.I),
]

# Explicitly unrelated topics (coding, weather, resume, science, generic trivia, recipes)
UNRELATED_PATTERNS = [
    re.compile(r'\b(python|javascript|java|c\+\+|code|coding|script|program|programming|function|array|class|algorithm|database|sql|html|css)\b', re.I),
    re.compile(r'\b(weather|temperature|forecast|rain|sunny|climate)\b', re.I),
    re.compile(r'\b(resume|cv|job interview|cover letter|career advice)\b', re.I),
    re.compile(r'\b(quantum|physics|chemistry|biology|astronomy|gravity|atom|molecule)\b', re.I),
    re.compile(r'\b(capital of|population of|gdp of|president of|prime minister of)\b', re.I),
    re.compile(r'\b(recipe|bake|baking|cook|cooking|dish|ingredient|cake|pasta|pizza recipe)\b', re.I),
    re.compile(r'\b(tell me a joke|funny joke|riddle)\b', re.I),
    re.compile(r'\b(crypto|bitcoin|stock|stocks|stock market|stock price|investment|forex)\b', re.I),
]


def is_football_query(query: str) -> bool:
    """
    Lightweight, deterministic local domain gate.
    Determines whether a user query is related to FOOTBALL/SOCCER IN GENERAL.
    Does NOT use LLMs, Groq tokens, RAG, or dataset lookups.

    Classification Principle:
    - Determine whether mathematics is being used IN A FOOTBALL CONTEXT.
    - Strong Football Signals (keywords, formations, teams, tactics, metrics) override generic math terms.
    - Standalone math queries ("What is 10 + 20?", "Solve x^2 + 5x + 6 = 0") -> REJECT locally.
    - Football math queries ("What is Arsenal's average goals per game?", "Calculate goal difference") -> ACCEPT.
    - Explicitly unrelated topics (coding, weather, resume, science, jokes) -> REJECT locally.
    - Short ambiguous follow-ups (<= 5 words) -> Prefer ACCEPT.
    """
    if not query or not query.strip():
        return False

    text = query.lower().strip()

    # 1. Detect Strong Football Signals
    has_football_signal = False

    if FORMATION_PATTERN.search(text):
        has_football_signal = True
    else:
        for kw in FOOTBALL_KEYWORDS:
            if " " in kw or "-" in kw or "'" in kw or "." in kw:
                if kw in text:
                    has_football_signal = True
                    break
            else:
                if re.search(r'\b' + re.escape(kw) + r'\b', text):
                    has_football_signal = True
                    break

    # 2. Check for Standalone Math Patterns
    for math_pattern in MATH_PATTERNS:
        if math_pattern.search(text):
            if has_football_signal:
                return True
            return False

    # 3. Check for Explicitly Unrelated Topics (coding, weather, resume, science, etc.)
    for pattern in UNRELATED_PATTERNS:
        if pattern.search(text):
            if has_football_signal:
                return True
            return False

    # 4. If a strong football signal is present, ACCEPT
    if has_football_signal:
        return True

    # 5. Check for short ambiguous queries / conversational follow-ups (<= 5 words)
    words = text.split()
    if len(words) <= 5:
        return True

    # 6. Fallback for longer queries: default ACCEPT to avoid false negatives on conversational queries
    return True

