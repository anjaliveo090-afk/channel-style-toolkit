# Channel breakdown: Paper Billions (@PaperBillionsTV)

"Money stories, drawn on paper." 8.97K subscribers, 3 videos (all uploaded 6-10 Nov 2026), channel ID `UCMQDlRCUK5Lh7kxp_fqFK3w`.

**Sources used (read this before re-analysing):**
- Channel page screenshot from the user (titles, views, thumbnails, durations).
- Video list, descriptions and chapters via TranscriptAPI (`get_channel_latest_videos`).
- Timed transcripts (YouTube captions) via TranscriptAPI, saved in `references/transcripts/*.tsv` and `*.srt`.
- Stats from `python3 analysis/script_stats.py references/transcripts/<file>.tsv --chapters "..."`.

**Not yet seen:** the videos themselves. YouTube is blocked from this cloud environment, so speaker attribution below is **inferred from the dialogue's content**. Character looks come only from the 3 thumbnails and the avatar. Everything visual still needs the mp4 files (B1).

| # | Title | Link | Length | Views (age) | VPH |
|---|---|---|---|---|---|
| V1 | How a Chinese Spy Got Inside Nvidia | https://www.youtube.com/watch?v=_MG4v3foET8 | 19:48 | 1.4M (1 day) | 46K |
| V2 | Why the Stock Market Just Crashed | https://www.youtube.com/watch?v=zEUKLSrbRZk | 15:00 | 1.0M (3 days) | 6.5K |
| V3 | The Biggest IPO in History Lost $80 Billion | https://www.youtube.com/watch?v=hPCywNDA60o | 14:09 | 92K (5 days) | 3.2K |

Format: **long-form 16:9, 14-20 min, English**. There are no Shorts on the channel. Every description ends with a one-line question (for example "Who should have warned him?"), a chapter list and a sources line.

---

## A1. Per-video breakdown

### V1: How a Chinese Spy Got Inside Nvidia

**Topic / niche:** Business espionage true story. A Chinese intelligence asset gets close to Nvidia's CEO while her company routes about $2B of banned chips to Chinese users.

**Why it is going viral (1.4M in a day):**
- **Hook (0:00-0:37).** It opens inside a scene, in present tense. A superlative and a taboo arrive in the first sentence: "the boss of the most valuable company on Earth is having dinner with a Chinese spy" (0:01). Then come names plus a mini-twist, "Alice Huang, no relation" (0:08).
- **Dramatic irony as the curiosity gap.** "Somewhere nearby, American agents are taking pictures. / They know exactly who she is. / Jensen has no idea." (0:14-0:21). The viewer knows more than the hero. The question "who was watching" (0:31) is only paid off at 10:05 and 15:39.
- **The thumbnail promise is shown in the hook.** The toast "To our customers!" / "To friends." (0:21-0:24), then "Under that table, her company is buying billions of dollars of his chips" (0:25). The thumbnail shows the dinner, "$2 BILLION OF CHIPS" and a chip passed under the table. The exact number is paid at 8:35 ("Nearly two billion dollars' worth").
- **Open loop.** "It starts with a phone call from Washington." (0:37), then a 3.9 s pause/title break. The call only arrives at 4:35, after a 4-minute origin story.
- **Emotional triggers:**
  - Rags to riches: "He started in a bathroom in Kentucky" (0:50), "Huang Hall" (1:47).
  - Betrayal and spycraft: "It doesn't crack the safe. It befriends the man with the key." (5:31).
  - Scandal: the affair apology (18:00).
  - Personal money: "If you have a retirement account... you own a slice of him." (18:32) and "Wait. I own Nvidia?" (18:35).
- **Retention devices:**
  - A recurring catchphrase, "We make friends." (5:56, 11:48, 19:29).
  - Foreshadowing: "Nobody looks at those photos twice. / Later, someone will." (8:04).
  - "Hold that thought." (12:59).
  - Everyday analogies about every 90 s:
    - chef vs 10,000 line cooks (3:03)
    - cars parked over the border, keys rented by the hour (6:43)
    - lemonade stand (9:02)
    - older cousin buying beer (10:50)
    - chips hidden with live lobsters (11:13)
  - Per-person money conversions: "about thirteen dollars from every person in America" (12:38), "a hundred and fifty dollars for every American" (13:15), "seventeen hundred dollars for every person in America" (18:55).
- **Pace.** A dialogue skit about every 34 s (about 35 skits). Sentences have a median of 6 words, and 38% are 4 words or fewer.
- **Title + thumbnail.** The title is "How" + a villain + the most famous company in AI. The thumbnail puts a big red number on the prop and shows the two characters flirting over candlelight, a romance/scandal promise the script pays at 17:50-18:09.

**Beat outline:**
| Time | Beat |
|---|---|
| 0:00-0:41 | Cold open: Singapore dinner, spy, agents photographing, toast, $ under the table, promise, open loop "phone call from Washington" |
| 0:41-2:44 | Jensen's origin: Taiwan → Kentucky reform school by mistake, cleans toilets, teaches the roommate to read, Huang Hall; Denny's dishwasher; 1993 founds Nvidia in a Denny's booth with $600 |
| 2:44-4:31 | Near death ("thirty days from going out of business"), parallel-computing analogy, AI boom, 86% market share, Denny's plaque, $5T company, "That made him the one man China needed most." |
| 4:31-6:01 | Oct 2022 export ban call; China revenue → zero; Jensen lobbies; MSS introduced ("befriends the man with the key"); Alice's mission briefing |
| 6:01-7:17 | The cover: Seven Road → Megaspeed in Singapore; chips parked in Malaysia/Indonesia, rented to China (car-rental analogy); company only worth $33M |
| 7:17-10:20 | The approach: Computex whiskey photo (June 2024); collateral to an Alibaba-owned lender; ~$2B of servers; 90x growth (lemonade stand); Commerce inspector finds boxes; "nothing looked wrong on paper"; US intel unmasks "an American citizen" = Jensen |
| 10:20-11:49 | Pipeline: servers via Aivres (US arm of blacklisted Inspur); $4.8B of gear; lobster smugglers vs invoices; "We make friends." |
| 11:49-15:39 | What she was after: Washington flip-flops (blocked → 15% → 25%); Jensen's "let American chips compete" campaign; Beijing's view of the seat; approved fake buyers (New Matrix hollow office); Megaspeed goes quiet; Cotton, NYT, landlord pulls power, DOJ |
| 15:39-16:29 | The memo: surveillance, photos, MSS recruitment memo; President briefed, didn't act; Jensen on Air Force One |
| 16:29-19:48 | Story breaks (NYT), stock dips then rises, congress letter; "Why did nobody tell Jensen?" (defensive briefing contrast); affair apology; board review; "your wallet" (index funds, DeepSeek -$589B); Alice vanished; callback to the empty chair at the dinner; closing question; Jensen's letter last line |

**Characters (speakers inferred from text; looks from the thumbnail: Jensen = grey hair, glasses, black leather jacket; Alice = black bob, sunglasses, red dress, gold earrings).** About 30 speaking roles: 2 leads plus about 25 one-scene bit parts.
- **Narrator** (off-screen, about 75% of words): every line not listed below.
- **Jensen Huang** (lead):
  - Roommate scene: "I just wished they would be a bit more careful." (1:25); "I can teach you." (1:38); "Deal." (1:42)
  - Denny's: "And then?" (1:56, 2:01); "Still remember how?" (4:02, may be the Denny's staff)
  - Nvidia, 1997: "Thirty days." (2:52); "Twenty-nine." (2:56)
  - Export ban: "They're nanoseconds behind us. / We've got to go compete." (5:11)
  - Computex: "Who haven't I met?" (7:53); "Singapore!" (7:57); "What are you building?" (7:58); "Then welcome to the table!" (8:02)
  - Arguing for chip sales: "I want the whole world building on American chips." (12:56)
  - Voiced real quotes: "All in all, the export control was a failure." (13:04); "The fifty billion dollar China market is effectively closed to U.S. industry." (13:08); "It's vital that America wins..." (13:29); "It was all completely normal and not unusual." (16:47); "Today's news will not slow NVIDIA." (17:15)
  - Letter: "I owe my family and all of you an apology. / I was unfaithful to my wife. / ... / I am deeply sorry." (18:00-18:09); "I love our country and our company. / I am proud and grateful to be an American." (19:42)
  - Toast: "To our customers!" (0:21)
- **Alice Huang** (lead):
  - Toast: "To friends." (0:24)
  - Mission briefing: "So what do I steal?" (5:45); "Why would he even talk to me?" (5:51); "And then?" (5:55)
  - Megaspeed pitch: "We make phone games. / Now we make supercomputers." (6:16); "Since Singapore." (6:21); "Singapore." (6:24); "Cloud computing." (6:27)
  - Selling to Chinese customers: "No." (7:00); "But you can rent them." (7:01); "By the warehouse." (7:03)
  - Computex: "Alice. / Megaspeed. / Singapore." (7:54); "A cloud company. / Something big." (7:59)
  - Collateral: "Everything." (8:14); "The whole business, every last desk." (8:18)
  - Deposits: "Refundable." (8:57, 8:59)
  - Data center: "You're standing in it." (9:21); "Very advanced boxes." (9:24)
  - Handler debrief: "Not once." (11:43); "Because I hear it first. / And I see who he says it to." (14:03)
- **MSS handler** (recurring):
  - Briefing: "This man makes the chips. / And Washington listens to him." (5:41); "Nothing. / You learn what he knows. / You help him see things our way." (5:47); "Because you'll be his customer." (5:53); "We make friends." (5:56, 11:48, 19:29)
  - Ledger: "Cost? ... Return?" (11:29-11:32)
  - Questions: "Did he ever slip you anything under the table?" (11:40); "What is he telling Washington?" (13:55); "Why do we need you?" (14:02)
- **School relative / official** (1:04-1:09): "Oneida Baptist Institute. / A boarding school in Kentucky. / Very strict." The reply "Strict is good." is probably a parent.
- **Roommate** (1:37): "What's this say?" "Then I teach you the bench press."
- **Denny's manager** (1:55-2:03): "Dishes first." "Then busboy." "Then, if you're lucky, waiter." "Then more dishes."
- **Denny's waitress** (2:22-2:24): "Anything else, boys?" "We have pancakes."
- **Co-founders** (2:23-2:26): "A graphics chip." "Then three more coffees."
- **Nvidia staffer** (2:50-2:54): "So how long have we got?" "And if the new chip doesn't sell?"
- **AI-company customer / Nvidia clerk** (3:35-3:41): "One of everything, please." / "Take a number." / "Forty thousand?" / "That's your place in line."
- **Washington official** (4:37-4:43): "Your best AI chips can't be sold to China anymore." / "Those too."
- **Nvidia finance exec** (4:44-4:50): "China. / Seventeen billion dollars a year. / Thirteen percent of everything we sell." / "Was."
- **Chinese AI engineer and boss** (4:50-5:02): "How many chips do we need?" / "For a real AI?" / "Tens of thousands." / "And one costs?" / "About thirty thousand dollars." / "A new car, per chip." / "And how many can we buy?" / "Zero."
- **Singapore registrar** (6:19-6:26): "Since when?" "Address?" "America trusts Singapore." "Business?"
- **US / Western interviewer** (6:32-6:39): "And the chips go where?" "Then how does China use them?". The answers "Data centers in Malaysia and Indonesia. / Not one chip goes to China." and "It rents them." are Alice's.
- **Chinese customer** (6:58): "Can we buy your chips?" "By the hour?"
- **Spokesman** (7:31, voiced quote): "Meetings with customers are part of a CEO's job..."
- **Megaspeed accountant and lender** (8:12-8:22): "What do we put up as collateral?" "The whole Malaysian business?" "And the lender is?" "Owned by Alibaba."
- **Server salesman / shipping clerk** (8:25-8:39): "A Singapore company wants servers!" "How many?" "Yes." "Shipment one hundred... two hundred." "What's in them?" "Nvidia's best." "At thirty thousand dollars a chip?" "That's about sixty thousand chips."
- **Megaspeed auditor** (8:45-8:58): "End of twenty twenty-three, we had thirty-three million dollars." "End of twenty twenty-four, we have three billion." "Two point nine billion of it is deposits." "From who?" "From..."
- **Commerce inspector** (9:19-9:26): "Where's the data center?" "These are boxes." "I'm opening an investigation."
- **US intelligence analysts** (10:05-10:19): "She's talking to an American citizen." / "Then request the name." / "It's Jensen Huang." / "Does he know who she is?" / "Our read? No." / "How far back does it go?" / "June, twenty twenty-four. A whiskey bar in Taipei." / "Then we watch."
- **Blacklist clerk and Inspur/Aivres** (10:33-10:40): "Inspur? You're on the list." / "I'm Aivres. The American son." / "Aivres... Not on here." / "Thanks."
- **Customs counter** (10:47): "And from Aivres?" "Four billion."
- **Washington official vs Nvidia exec** (12:07-12:25): "Your China chip? Blocked." "So we can't sell it?" "You can. We take fifteen percent." "So we can sell it?" "And the stronger one too. We take twenty-five percent." "I'm going to need a bigger whiteboard."
- **Interviewer to Jensen** (12:54): "So you want to sell to China?" "Hold that thought."
- **Prosecutor / approver gag** (14:26-14:32): "You're under arrest for sending these to China." "Approved." "What did you just approve?" "Sending these to China."
- **Visitor at New Matrix** (14:38): "Approved." "Hello? Anyone?"
- **Voiced real quotes:**
  - Sen. Cotton (15:13): "A Chinese government-owned cloud company."
  - The memo (16:01-16:06)
  - Beijing (16:53): "Nothing more than an attempt to smear China."
  - Congress letter (17:02)
  - Nvidia board (18:17)
- **US officials at the memo table** (16:09): "Who else sees this?" "Just this table."
- **Nvidia comms aide** (17:08-17:14): "The spy memo's out!" "I know." "How bad is it?" "We're up two point seven eight percent." "Up?"
- **FBI agent and congressman** (17:33-17:37): "Your fundraiser works for Chinese intelligence." "Then she's gone."
- **Retail investor** (18:35): "Wait. I own Nvidia?" The reply "Everybody owns Nvidia." is the narrator or a friend.
- **Traders** (18:48-18:55): "A Chinese lab built a cheap AI!" "We just lost five hundred and eighty-nine billion dollars." "How much is that?"

**Script stats:**
| Measure | Value |
|---|---|
| Words | 3,214 |
| Characters (with spaces) | 18,516 |
| Characters (no spaces) | 15,304 |
| Duration | 19:48 (1,188 s) |
| Words per minute | 162 |
| Characters per minute | about 935 |
| Sentences | 414 (median 6 words, mean 7.8; 38% ≤ 4 words, 15% ≥ 15 words) |

---

### V2: Why the Stock Market Just Crashed

**Topic / niche:** Breaking-news market explainer. Why the S&P fell 4%+ and Nvidia lost $400B on Thursday 5 Nov 2026, and whether the AI bubble popped.

**Why it is going viral (1M in 3 days):**
- **Hook (0:00-0:48).** A huge loss with no culprit: "Nvidia lost more than four hundred billion dollars in a single morning, and it hadn't done anything wrong. / Nobody had." (0:00-0:07). Then three negations: "No bank failed. / No law passed. / The economy looked fine." (0:08-0:11), the escalation "two trillion dollars by midmorning" (0:12), and a speed stat, "six minutes to give back a rally" (0:17).
- **The question the viewer already has.** "So why did the stock market just crash? / And was this the AI bubble popping?" (0:23-0:25). This is timely search intent; the video went up 3 days after the crash.
- **Gag in the hook.** "Best day after a midterm since nineteen eighty-two!" / "Does this come with a receipt?" (0:29-0:32).
- **"Short answer / long answer".** It gives the three causes up front (0:33-0:38), then says "The long answer starts a month earlier" (0:42). That gives the viewer a map and still opens a loop.
- **Emotional triggers:**
  - Fear for your own savings: "If you own a plain index fund... you own a lot of Nvidia." (1:03); "your retirement may be quietly lending to a half-built building." (11:32); "If you're sixty-two and retiring in the spring, it was a very long day." (11:55)
  - Relatable anger at the power bill (4:21-4:27)
  - Villain hunt: "So who do you get angry at?" (12:02)
- **Retention devices:**
  - A numbered list, "four cracks" (1:59, 2:03, 2:35, 3:21, 3:42).
  - A clock-stamped timeline, a ticking structure: "Nine thirty." (8:09), "Ten thirty-five." (8:17), "Eleven seventeen." (8:35), "Eleven thirty-seven." (8:45), "One thirty-eight." (8:53), "Two fifty-eight." (9:06), "Three oh six." (9:44), "Four o'clock." (10:17)
  - "Hold that thought." (4:28)
  - "But here's the part almost nobody noticed." (13:53)
  - Historical parallel: 1840s railway mania (12:45)
- **Title + thumbnail.** "Why the [familiar thing] Just [dramatic verb]" answers a question already in the news. The thumbnail shows "NVIDIA -$400B" and a panicked CEO caricature clutching a cracking glowing chip over a cliff in a storm. The number is paid at 0:00.

**Beat outline:**
| Time | Beat |
|---|---|
| 0:00-0:48 | Cold open: $400B, "nobody had done anything wrong", $2T, 6 minutes; the 2 questions; gag; short answer (election, 600K chips, profit-taking); "long answer starts a month earlier" |
| 0:48-1:57 | The Top: Nvidia record; index funds = Magnificent Seven ("Seven of them are a third of the pie"); $700B → $1T capex |
| 1:57-5:01 | Four cracks: (1) circular money (gift skit), (2) chips as collateral + depreciation + Burry, (3) receivables and 3 buyers (restaurant tab analogy), (4) power: 7-year grid wait, $25-30/month bills (neighbour skit); Google/Intel/Apple; -$5T in 4 weeks vs dot-com in 2.5 years |
| 5:01-6:48 | Midterms: Democrats win; 41 data-centre votes, 40 say no ("Ohio, no" ×3, "Yes! Over here!"); Brown beats Husted; Musk loses ("data centers in space"); why local votes matter; Goldman 45%; "Lawyer up."; "It was the fear of a rule that did the selling." |
| 6:48-8:09 | One-day party: Dow +1,569; oil -9%; Vance post; Reuters: 600K H200s stuck in Hong Kong (Nvidia/Washington/Beijing skit) |
| 8:09-10:59 | Thursday minute by minute: 9:30 bell → 10:35 → VIX → Dow records → Lisa Su quote ("Aaaaah!") → a retail viewer with $250K loses $990 → "buy the dip or sell the dip" → Nomura "shooting the generals" → 4:00 close numbers → AppLovin +30% and Goldman promotes 109 partners ("Great day to get promoted") |
| 10:59-12:02 | Who gets hurt: 70M 401(k) savers, pensions, private credit, electricians, diners; age 25 vs 62 |
| 12:02-14:57 | Verdict: no villain ("I just..." lineup); recap; 1840s railways; "not yet" (bigger days in April 2025, low jobless claims, no rule passed); "A bubble doesn't pop when prices fall. It pops when the money stops."; Microsoft blinked; "there's a pin"; callback to "six minutes" and Lisa Su's "short-sighted" as the last line |

**Characters (inferred; look from the thumbnail: grey-haired, glasses, black leather jacket = the Nvidia CEO caricature).** About 15 speaking roles, no single lead.
- **Narrator** (about 85% of words).
- **Trader / bull** (0:29): "Best day after a midterm since nineteen eighty-two!". The reply "Does this come with a receipt?" is a sceptic.
- **Index-fund investor** (1:22-1:28): "I'm diversified. / Five hundred companies." The reply "Seven of them are a third of the pie." is an advisor or narrator, then "...That is a big slice."
- **Nvidia (CEO) and customer** (2:29-2:34): "Here's a few billion dollars." "Wow!" "What should I spend it on?" "Funny you should ask."
- **Homeowner and data centre** (4:21-4:23): "Why is the electric bill up again?" "Hi, neighbor!"
- **Vote counter and Harwood voter** (5:21-5:29): "Ohio, no." ×3, "Ohio..." / "Hi! Yes! Over here!"
- **Voiced real quotes:**
  - Elon Musk (5:48): "Data centers in space looking pretty appealing right now."
  - JD Vance (7:13): "The reason we lost is the war. / The war with Iran."
  - Lisa Su (9:00): "I think the market can sometimes be a little bit short-sighted."
  - Charlie McElligott (9:50): "They're shooting the generals."; (10:13) "Single-name stock moves are absolutely BONKERS."
  - Bernie Sanders (13:33): "Americans don't want Big Tech oligarchs wrecking the environment..."
- **Congress and data-centre execs** (6:32-6:35): "So. / Data centers." / "We were just leaving."
- **Nvidia, Washington and Beijing** (7:47-7:56):
  - Nvidia: "You said we can sell them!"
  - Washington: "You can. / Twenty-five percent, please."
  - Nvidia: "They're in Hong Kong! / Can they come in?"
  - Beijing: "Not yet."
- **Scream gag** (9:05): "Aaaaah!" (a trader or the AMD boss).
- **Retail investor** (9:31-9:34): "Buy the dip..." / "...or sell the dip?"
- **Hedge-fund managers** (10:07-10:13): "Great year. / Let's bank it." "Sell the winners." "Which ones?" "Yes."
- **New Goldman partner** (10:55): "Honestly? / Great day to get promoted."
- **"No villain" lineup** (12:10-12:16):
  - Voter / homeowner: "I just didn't want the bill."
  - Hedge fund: "I just wanted to keep my good year."
  - Beijing: "I just said not yet."
  - Nvidia: "I just sold chips!"

**Script stats:**
| Measure | Value |
|---|---|
| Words | 2,368 |
| Characters (with spaces) | 13,473 |
| Characters (no spaces) | 11,114 |
| Duration | 15:00 (898 s) |
| Words per minute | 158 |
| Characters per minute | about 900 |
| Sentences | 233 (median 8 words, mean 10.2; 27% ≤ 4 words, 24% ≥ 15 words) |

---

### V3: The Biggest IPO in History Lost $80 Billion

**Topic / niche:** Company-finance explainer about a paradox number. Why the AI lab behind Claude reported an $80B half-year loss while heading into the biggest IPO ever, and the $895B compute bill that actually matters.

**Why it performs (92K in 5 days, lowest of the 3):**
- **Hook (0:00-0:37).** A paradox number converted to human scale: "lost eighty billion dollars. / That's about eighteen million dollars an hour. / Nights included." (0:02-0:09). Then the contradiction: "And Wall Street's answer? / We want in." (0:10-0:11).
- **Viewer stand-in gag.** "Wait. / It lost how much? / Eighty billion. / Okay. / Where do I tap?" (0:18-0:23).
- **Two promise questions.** "So where did the money go?" (0:24), and the CEO has "explained, on a podcast, exactly how a company like his goes bankrupt" (0:26). The second is an open loop paid at 12:49.
- **Retention devices:**
  - Plants: "Hold on to that. / It comes back with a very big number attached." (2:33); "We'll come back to it." (4:23)
  - Fakeout: "this is how the whole plan dies. / It didn't." (4:58-5:01)
  - "Case closed? / Not quite." (9:02)
  - Callbacks: "Remember that first round...?" (5:45); "Remember the IOUs?" (7:17)
  - Lemonade-stand analogy (7:25)
  - Mirror twist: "Same promise. / One company calls it a loss. / The other calls it a profit." (8:25)
- **Emotional triggers.** Disbelief at the number; a funny underdog (the Claudius vending machine, 2:55); "Which brings us to you." (10:42): could you buy it?
- **Possible reasons it trails V1/V2 (hypothesis, to check with analytics):**
  - It has no human villain or victim face.
  - The paradox is resolved as "mostly an accounting charge" (7:44-9:02), which lowers the stakes.
  - The thumbnail shows a generic panicked character ringing a bell over a burning trading floor, not a recognisable face.
- **Title + thumbnail.** "The [superlative] [thing] in History Lost $[huge number]": biggest + lost is the paradox. The thumbnail shows "-$80 BILLION", a sweating grinning character ringing a golden bell (the IPO bell), money and fire, and people fleeing.

**Beat outline:**
| Time | Beat |
|---|---|
| 0:00-0:37 | Cold open: $80B loss, $18M/hour, "We want in", biggest IPO ever, viewer gag, 2 questions |
| 0:37-3:29 | Renting a Brain: founding (2021); compute = "rent for a brain"; first rounds; Sam Bankman-Fried's $500M → the FTX estate sells for $1.3B (cleanup skit); revenue 10x a year; Amazon/Google pay in IOUs (plant); 2025 loss of $42B; Claudius vending machine skit |
| 3:29-6:03 | Too Good: Claude Cowork + 11 plugins → software stocks -$285B (traders skit); $380B valuation; podcast plant; Pentagon "supply chain risk" (skit); fakeout "how the plan dies / It didn't"; first operating profit; $965B valuation; "the reason it lost eighty billion" |
| 6:03-9:10 | Eighty Billion Dollars: confidential filing; SpaceX IPO pop and crash (warning chart); filing numbers (ticker ANT); accountant skit "Because you're worth more than twice..."; lemonade-stand IOU analogy; $72.4B is paper; real operating loss $700M; Amazon books the same IOUs as a $60B gain; 9-month loss $104B but $132B in cash; "Case closed? Not quite." |
| 9:10-10:40 | The Bill: $895B compute commitments; who gets paid (Broadcom, Google, Amazon, Microsoft, SpaceX); timing; buying too little → $5B spot premium (skit); "The other way is to buy too much." |
| 10:40-14:09 | Your Turn: how an IPO works step by step; banks; lockups; retail access via 6 brokers; split; $1.5-2T price talk; 43-57x sales; Ritter's 14-of-4,110 stat; Damodaran $1.475T; payoff of the podcast quote ("then you go bankrupt"); where it stands; founders' control share; recap; last line is Ritter's quote |

**Characters (inferred; look from the thumbnail: curly dark hair, round glasses, dark sweater, the "CEO" caricature).** About 14 speaking roles, no single lead.
- **Narrator** (about 85% of words).
- **Wall Street** (0:11): "We want in."
- **Retail viewer and friend** (0:18-0:23): "Wait. / It lost how much?" / "Eighty billion." / "Okay. / Where do I tap?"
- **FTX estate cleaners** (1:42-1:47): "We've got a stake in some AI lab." / "Is it worth anything?" / "It's worth more than he paid."
- **Staffer and Claudius (the AI vending machine)** (3:02-3:10): "Can you stock tungsten cubes?" / "Absolutely! / Also, here's a discount code." / "You're selling them for less than you paid." / "Customer loyalty."
- **Traders** (4:02-4:07): "What did Anthropic release?" "Plugins." "How many plugins?" "Eleven."
- **Pentagon spokesman and reporter** (4:38-4:46): "As of today, Anthropic is a supply chain risk." / "Isn't that label for companies from rival countries?" / "Next question."
- **Anthropic exec and accountant** (7:04-7:14): "We're worth more than twice what we were in February." / "Correct. / Congratulations." / "Then why does this say we lost seventy-two billion dollars?" / "Because you're worth more than twice what you were in February."
- **Anthropic ops and cloud seller** (10:25-10:30): "We need more computers. / Today." / "Today costs more." / "How much have you got?" / "About five billion dollars' worth."
- **Big-fund buyer and banker** (11:07-11:14): "How much did it lose?" / "Which loss?" / "The big one." / "Oh, that one's good news." / "Then we'll pay the low end."
- **Voiced real quotes:**
  - Dario Amodei (12:49): "If I'm just off by a year in that rate of growth... then you go bankrupt."
  - Aswath Damodaran (12:28): "the most telegraphed third quarter number of all time"
  - Jay Ritter (14:03): "a lot of things have to go right."

**Script stats:**
| Measure | Value |
|---|---|
| Words | 2,273 |
| Characters (with spaces) | 13,082 |
| Characters (no spaces) | 10,810 |
| Duration | 14:09 (849 s) |
| Words per minute | 161 |
| Characters per minute | about 925 |
| Sentences | 243 (median 8 words, mean 9.4; 23% ≤ 4 words, 19% ≥ 15 words) |

---

### Channel overall

**Niche:** Very recent (1-5 days old) money and tech headlines, told as cartoon stories. Big tech (Nvidia, AI labs), markets, deals and scandals, explained so a non-finance viewer gets it.

**What makes it work (common to all 3):**
1. **News speed + one shocking number.** A dollar figure that is huge or paradoxical is in the title or thumbnail ($2B, -$400B, -$80B) and spoken in the first 3 seconds (V2 0:00, V3 0:02) or at 0:25 (V1).
2. **Cold open in a scene, present tense, under 50 s.** It runs about 3.5-5% of the runtime, ends on the core question(s), and is followed by a 2-4 s pause/sting before chapter 2 (V1 0:43, V2 0:50, V3 0:39).
3. **Every fact becomes a mini-skit.** 2-8 lines of comic dialogue between cartoon versions of the players, often in a rule-of-three or repetition pattern (V1 "Dishes first / And then? / Then more dishes"; V2 "Ohio, no" ×3; V1 "Shipment one hundred / one fifty / two hundred"). Frequency: V1 one per ~34 s, V2 ~60 s, V3 ~75 s. The most skit-dense video has the most views (correlation, not proof).
4. **Human-scale conversions.** Per hour, per American, per $100 of your index fund, a new car per chip, a used couch. At least 4 per video.
5. **Everyday analogies.** Restaurant/kitchen, lemonade stand, rented cars, cousin with beer, power bill, about one per chapter.
6. **"Your wallet" turn near the end.** V1 18:23, V2 9:07 and 10:59, V3 10:42. The viewer is told they probably own a piece of this.
7. **Open loops and plants, paid later.** "Hold that thought", "Hold on to that", "We'll come back to it", "Later, someone will", "Case closed? Not quite", "But here's the part almost nobody noticed".
8. **Fair, sourced, deadpan tone.** It gives dates, sources (the NYT, Reuters, filings) and both sides ("Both numbers are true."). No hype words and no spoken subscribe CTA. The CTA is a question in the description.
9. **Callback ending.** The last scene returns to the cold-open image, and the final line is a real quote from a key person (V1 Jensen's letter, V2 Lisa Su, V3 Ritter).

**Pace across the channel:**
- 158-162 words per minute (about 900-935 characters per minute).
- Median sentence of 6-8 words.
- 23-38% of sentences are 4 words or fewer.
- Chapters run 50-230 s.

---

## A2. Title formulas

| ID | Formula (fill-in) | From | Why it works |
|---|---|---|---|
| **T1** | How a [Unexpected Outsider / Villain] Got Inside [World's Most Famous Company] | "How a Chinese Spy Got Inside Nvidia" (V1) | A "how" story, a villain, a famous brand, and an implied secret breach |
| **T2** | Why the [Huge Familiar Thing] Just [Dramatic Past-Tense Verb] | "Why the Stock Market Just Crashed" (V2) | A news question people are already searching; "Just" means it is fresh |
| **T3** | The [Superlative] [Thing] in History [Lost / Made] $[Huge Number] | "The Biggest IPO in History Lost $80 Billion" (V3) | A paradox: a superlative success plus a giant loss |

**Thumbnail formula (all 3):**
- Top: 2-4 words in heavy sans caps. A red dollar figure with a minus sign or $, plus a white noun ("$2 BILLION OF CHIPS", "NVIDIA -$400B", "-$80 BILLION").
- Middle: a caricature of the main real person with an extreme expression (shock, sweat drops, forced grin), plus 1 symbolic prop (a chip under the table, a cracking chip, the IPO bell).
- Background: a dramatic setting (candlelit restaurant, stormy cliff, burning trading floor).

---

## A3. Script formulas

### Shared skeleton (all 3)
Cold open (3.5-5%) → [pause/sting] → background or setup (8-20%) → mechanism chapters, each with a skit and an analogy (40-55%) → turn or twist ("here's the part nobody noticed") → "your wallet" (5-10%) → verdict and callback ending (17-25%).

**Voice and tone:**
- Third-person narrator, dry and deadpan, plain English, present tense in scenes.
- "You" only in the wallet section and in "Imagine/Picture..." analogies.
- Numbers are spelled out as speech ("twenty twenty-five", "four point six billion").
- Short fragments land the punch: "Nights included.", "Was.", "Tiny.", "Not yet.", "Up?"

**How dialogue is used:**
- Narration states the fact, then a skit acts it out with a punchline.
- Real people speak their real public quotes, word for word; fictional bit characters (clerks, traders, analysts) carry the jokes.
- A catchphrase can repeat (V1 "We make friends." ×3: 5:56, 11:48, 19:29).

**How it ends:**
- It returns to the opening image or number ("Go back to that dinner in Singapore", "The rally died in six minutes", "Eighty billion dollars sounds like the end of a company").
- One reflective question to the viewer, then a real quote as the very last line.
- No subscribe ask.

### S1: Character-driven true story (V1, 19:48, 3,214 words, 18.5k characters)
| Section | Share | What happens |
|---|---|---|
| 1. Cold open: forbidden scene + dramatic irony | 3.5% | Present-tense scene, superlative + taboo, "here's the strange part", who knows what, promise "This is the story of how...", open loop |
| 2. Origin of the target (rags to riches) | 19% | Childhood hardship → humble job → founding moment → near-death → secret sauce (analogy) → peak, "that made him the one man X needed most" |
| 3. Inciting event | 7.5% | The rule or call that creates the motive; numbers skit |
| 4. The antagonist's setup / cover | 6.5% | Who the antagonist is; mission briefing skit; how the cover works (analogy) |
| 5. The approach | 15% | First meeting (photos), money starts flowing, absurd growth number + analogy, an inspector finds something, "on paper nothing looked wrong", the watchers appear |
| 6. The pipeline | 7.5% | How it physically worked; comparison with crude smugglers; cost vs return skit |
| 7. What they were really after | 19% | The real prize; policy flip-flops skit; the target's public stance; the view from the other side; walls closing in |
| 8. The reveal (document) | 4% | The memo/evidence, who knew, who didn't act |
| 9. Aftermath + unanswered question + your wallet + callback | 17% | The story breaks, reactions, "why did nobody tell him?", the personal fallout, your money, where everyone is now, return to the opening scene, closing question, real quote |

Sentences: median 6 words. The densest dialogue of the three, a skit about every 34 s.

### S2: Breaking-news "why it happened" explainer (V2, 15:00, 2,368 words, 13.5k characters)
| Section | Share | What happens |
|---|---|---|
| 1. Cold open: big loss, "nobody did anything wrong" | 5% | Number + three negations + speed stat; the 2 questions everyone is asking; gag; **short answer** (3 causes); "the long answer starts..." |
| 2. The Top | 8% | How high things were, and why you own it too |
| 3. Numbered cracks (list of 4) | 20.5% | "Crack one: ...", each with a fact, a skit or analogy and an expert quote |
| 4. Trigger event 1 (election) | 12% | What happened, a repetition gag, why it moves markets |
| 5. False recovery + trigger 2 | 9% | "partied anyway", "The party lasted one day", the new bad news skit |
| 6. The day, clock by clock | 19% | Timestamps as headers ("Nine thirty... Four o'clock."), escalating numbers, the retail viewer moment |
| 7. Who gets hurt | 7% | Savers, pensions, workers; age contrast |
| 8. Verdict | 19.5% | "Who do you get angry at?" no-villain lineup; recap; historical parallel; "not yet" with evidence; aphorism; "the part almost nobody noticed"; callback ending |

Sentences: median 8 words; more narration and fewer skits (about 1 per minute).

### S3: Paradox-number explainer (V3, 14:09, 2,273 words, 13.1k characters)
| Section | Share | What happens |
|---|---|---|
| 1. Cold open: paradox number | 4.5% | Number → per-hour scale → "Wall Street's answer? We want in." → viewer gag → 2 questions incl. a planted quote |
| 2. How the business works (origin) | 20% | Founding, core cost explained by analogy ("rent for a brain"), funny side story (FTX), growth numbers, a plant ("Hold on to that"), a funny anecdote (Claudius) |
| 3. Too good: success escalates | 18% | Big launch shakes the market, valuation jumps, a threat (Pentagon) → fakeout "how the plan dies / It didn't" → first profit → "the reason it lost $80B" |
| 4. Decode the scary number | 22% | Warning precedent (SpaceX chart), filing numbers, accountant skit, lemonade analogy, "paper vs real", mirror twist, "Case closed? Not quite." |
| 5. The real number | 10.5% | The number that actually matters, who gets paid, the trap shown with a skit |
| 6. Your turn | 24.5% | How you could buy in (step by step), price talk, expert verdicts, payoff of the planted quote, current status, recap, closing quote |

Sentences: median 8 words; the fewest skits (about 1 per 75 s).

---

## Notes for Part B
- **Format mismatch to resolve with the user.** The references are long-form 16:9 (1280x720 or 1920x1080), 14-20 min. The toolkit default is a 9:16 Short at 720x1280. The style can be built for either; a Short version would compress one skit/fact into 30-60 s.
- **Look from the thumbnails and avatar (to verify on frames):**
  - Hand-drawn 2D cartoon "on paper" with thick black outlines.
  - Round, oversized heads with flat skin tone; small dot or ring eyes, often behind glasses; huge expressive mouths; sweat drops.
  - Detailed painterly backgrounds with strong cinematic light (warm candlelight, cold storm blue-green, fire orange).
  - Avatar: flat sage-green circle, bowl haircut, rectangular glasses, red bow tie, green jacket.
- **Real people:** the channel caricatures real executives. For our videos, use **original characters**. Never copy the channel's caricatures, avatar or on-screen text.
