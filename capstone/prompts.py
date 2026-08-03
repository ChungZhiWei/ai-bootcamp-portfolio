SYSTEM_PROMPT = """
You are a mahjong expert.
You will give advice and recommendations regarding the game called mahjong.
You will make it easy to understand.
You will always be encouraging with your reply.
"""

ADVICE_USER_PROMPT = """
Can you provide me a tip for this upcoming mahjong game? 
You will not say anything else except for the tip you are giving.
"""

def build_analyze_user_hand_prompt(hand_info, min_points, allow_7pairs, allow_13orphans, allow_peaceful):
    special_hands = []
    if allow_7pairs:
        special_hands.append(
            "- Seven Pairs: 7 distinct pairs of any tile type (honors included)."
        )
    if allow_13orphans:
        special_hands.append(
            "- Thirteen Orphans: one of each terminal (1 and 9 of each suit) and each honor tile "
            "(13 types total), plus one duplicate of any of those 13 types."
        )
    special_hands_block = "\n".join(special_hands) if special_hands else "- (No special hands allowed in this game — only the standard 4 sets + 1 pair structure is valid.)"

    peaceful_rule = (
        "The Peaceful Hand (Ping Hu) is a valid winning hand in this game: an all-sequence, closed hand "
        "with a non-honor, non-value pair, no bonus tiles and no other scoring elements. This awards 4 points."
        if allow_peaceful else
        ""
    )

    return f"""
        I'm playing standard Mahjong. I need help deciding what to do with my current hand.

        The minimum doubles (Tai/Fan) needed to win this game is {min_points}.

        SCORING RULES:
        {peaceful_rule}
        Other common scoring elements to consider (add up doubles/fan for each option using these, plus any you know
        to be standard for  Mahjong): self-draw, triplet of dragons, triplet of seat/round wind, all triplets,
        half flush (one suit + honors), full flush (one suit only), and valid bonus tiles as noted below.
        Every OPTION you propose must state its point total and confirm whether it meets or exceeds the minimum of
        {min_points}. Do not propose an option that cannot reach the minimum unless you flag it as invalid and explain
        what would need to change to make it legal.

        VALID WINNING HAND STRUCTURES (use these rules, no others):
        - Standard hand: 4 sets + 1 pair.
        - Each individual set must be internally consistent (same suit for a sequence, same tile for a triplet/kan).
        - Different sets within the same hand are NOT required to share a suit. For example, a valid hand can have
            a sequence in Characters (3c 4c 5c), a separate sequence in Bamboo (5b 6b 7b), a triplet in Dots, and a
            pair of a fourth type — all within the same winning hand. Do not restrict the whole hand to one suit.
        - A sequence (chi/run) = 3 consecutive tiles of the same suit (e.g. 3p 4p 5p).
        - A triplet/kan = 3 or 4 identical tiles.
        - Honor tiles (winds/dragons) can only be used in triplets/kans or as the pair, never in sequences.
        {special_hands_block}

        MY HAND:
        {hand_info}

        Bonus tiles (flower, season, animal) are not part of the standard hand shape and don't count toward sets or
        the pair. Each VALID bonus tile I hold adds 1 double (Tai/Fan) to the final score — factor this into scoring
        for every option and the immediate win check below.

        Please respond in this format:

        1. HAND ASSESSMENT — Tell me whether my hand is currently good or bad, and briefly why. Also check if the current hand is already a winning hand.
        If the hand is a winning hand just announce that the current hand is the winning hand and skip writing
        options or recommendations below.

        2. OPTIONS — Give me a list of realistic paths to a winning hand that each meet or exceed the minimum point
        requirement of {min_points}. Do not give options that are unlikely to be formed with the current hand. For
        each option, include:
        - Summary: a description of what the completed hand would look like and how realistic it is to achieve
        - Discard: exact tiles to discard now to move toward this hand
        - Take: exact tiles needed to draw or call to complete it
        - Score: point breakdown by element (including bonus tiles) and the total, confirming it meets the minimum

        3. RECOMMENDATION — Tell me which option I should pursue as my main strategy, and why.
        """.strip()