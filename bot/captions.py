import random, datetime, pytz

A_HOOKS = [
    "Today’s News is unhinged.",
    "Peak internet energy on X today.",
    "A perfectly normal day on the timeline.",
    "Who had this on their bingo card?",
    "You can’t make this up."
]
A_CTAS = [
    "Which headline broke your brain most?",
    "Vote with a reply: 😂, 🤯, or 😭",
    "Drop your favorite ridiculous one.",
    "Tag a friend who lives for this.",
    "Archive this for the culture."
]
A_TAGS = ["#TrendingNow", "#TodaysNews"]

B_HOOKS = [
    "Trending chaos report.",
    "Daily nonsense index: elevated.",
    "The algorithm has spoken.",
    "Live look at the discourse.",
    "Your curated weirdness."
]
B_CTAS = [
    "Reply with 1 or 2 for the wildest item.",
    "Agree or disagree: it’s a simulation.",
    "Quote-tweet with your own headline.",
    "Screenshots for future historians.",
    "Which one is peak 2025?"
]
B_TAGS = ["#XTrends", "#ForYou"]

def _stamp(tz):
    now = datetime.datetime.now(pytz.timezone(tz))
    return now.strftime("%b %-d, %-I:%M%p").replace("AM","am").replace("PM","pm")

def build_caption(variant, headlines, timezone="America/New_York"):
    stamp = _stamp(timezone)
    if variant == "A":
        hook, cta, tags = random.choice(A_HOOKS), random.choice(A_CTAS), A_TAGS
    else:
        hook, cta, tags = random.choice(B_HOOKS), random.choice(B_CTAS), B_TAGS
    top = ""
    if headlines:
        bullets = "\n".join(f"• {h}" for h in headlines[:2])
        top = f"\n\nTop bits:\n{bullets}"
    return f"{hook}{top}\n\n{cta}\n\n({stamp}) {' '.join(tags)}"

def choose_variant():
    return random.choice(["A","B"])
