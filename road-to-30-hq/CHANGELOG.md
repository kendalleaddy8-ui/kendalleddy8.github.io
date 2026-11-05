# Road to 30 HQ · changelog

The HQ itself lives as a private Claude artifact (it holds personal data, so its source is
intentionally not stored in this public repo). This file records what changed and when.

## v16 · Voices that work, Ventures, the '60s and '70s, a new cover (2026-11-05)

- **Voice built into HQ.** Deacon, The Executive and the crew speak with the phone's own voices. The old outside voice pages couldn't get the microphone inside the Claude app, which is why calls never connected. You talk back with the mic key on your keyboard.
  - **Each voice has its own sound.** Deacon is deep, slow and comforting. The Executive is crisp and always a different voice from Deacon. Each has a picker and a "Hear him" button.
  - **Voice hub on Home:** one tap to Deacon, The Executive (the faith gate, then the mock interview), the crew, or a voice check that tests what works on this phone.
  - **iPhone fixes:** a first tap unlocks speech, the first line no longer gets swallowed, and long answers no longer stall.
- **Ventures tab.** Five engines toward a $10K month each: Forward Works AI, Flow (tankless water heaters), Storefront (Shopify), the Markets desk and The Kit (digital products).
  - **Each has a plan:** straight-talk odds, an architecture, a sustainability plan, a ramp to April 29 and a week-1 checklist.
  - **Live scoreboard:** revenue comes from paid invoices, now tagged by business in the Office.
  - **Tools:** Flow's quote calculator (price, parts, labor, profit per install), a paper-trading journal with win rate and expectancy, and the Shopify store hookup.
  - **Three new crew members:** Flow (water heater trade lead), Shelby (storefront operator) and Dalton (markets teacher and risk manager), each with a backup.
  - **Honest by design.** No bot trades real money from HQ. Dropshipping odds are stated plainly. Water heater work starts with licensing and insurance.
- **Two new scheduled tasks.**
  - Dalton's pre-market brief every weekday at 7:27 AM. It shows on top of the Markets desk.
  - Flow's lead finder every Thursday evening: 8 water heater leads with drafted first messages, straight into the pipeline.
- **'60s and '70s eras:** Space Age '65 and Soul '72.
- **New cover:** a new app icon and a lock-screen wallpaper (gold 30, NO FEAR, the faith lines and the covenant), with a Shortcuts automation that sets the lock screen every morning.
- **Make it yours:** a Profile card sets the name and tagline in the header. First step toward a version anyone can download.
- **Built to hand off:** a private Source Kit holds every source file and a step-by-step guide, so a later session can rebuild, test and ship HQ without the original.

## v15 · Every tab as a launcher (2026-11-04)

- **Same pattern as Home, on every tab.** The main card stays up top, the rest become icon buttons ("More in Mind", "More in Money"), and each opens on its own with a "‹ Tab" back bar.
  - **Today:** momentum, today's workout and Deacon.
  - **Board:** the board and the task list.
  - **Learn:** today's lesson.
  - **Interview:** the pursuit card.
  - **Crew:** your team.
  - **Mind:** the Forge.
  - **Body:** today's plan.
  - **Work:** the Office.
  - **Money:** the summary, with the family budget as the first button.
  - **PLV:** the Booth door and the episode board.
  - **Life:** the decision.
  - **Schedule:** my day.
  - **Log:** tale of the tape.
- **Icons:** picked from each section's topic. **Labels:** each card's own heading.
- **Links still land in the right place:** any link into a tab (Ask HQ, quick actions, Privacy, pipeline form) opens the right card directly. Switching tabs resets. "Show everything" brings back the full scroll everywhere.
- **Not changed:** the Booth and Us were already one screen.
- **Typical tab height on a phone:** from 5,000 to 14,000px down to 400 to 2,600px.

## v14 · Home as a launcher (2026-11-04)

- **Home shows only what matters right now:** the "Right now" card, the Day 1 card (first week) and the quick actions. Everything else is one tap away as a big icon button.
- **"Right here" buttons:** each opens that Home card on its own screen, with a sticky "‹ Home" back bar. There are 18 of them: Missions, Rank, Lesson, AI video, Radar, Board, Inbox, Crew, Soundtrack, The Stash, The Signal, Fight Night, On the line, Shutdown, Inspire, Rewards, Journey and Letters. Each shows a live status line (XP today, rank, today's lesson, days to Fight Night).
- **"Go to" buttons:** they jump to every tab: Today, Mind, Body, Work, Money, Interview, Learn, Booth, PLV, Us, Crew, Schedule, Life, Board, Log and Privacy, plus Ask HQ.
- **Works in every mode:** night, wind-down and family modes. Shortcuts (Soundtrack, links) open the right card directly. "Show everything" brings back the long scroll.
- **Home height:** from about 12,700px to about 2,400px on a phone.

## v13 · Loyal crew, coverage, and the momentum engine (2026-11-04)

- **Loyalty oath** in every in-app agent call (Deacon, crew, huddles, lessons, everything): serve Kendall only, never deceive, never hide a failure, never take anyone else's side, cover for a downed teammate and say so. The Watchtower and the morning brief carry it too.
- **Coverage when an agent goes down:**
  - **In HQ:** calls retry on the ultimate model with backoff, then fall back to the best available model so the job still gets done. Calls you stop yourself, and refusals, are never retried.
  - **Crew chat:** if an agent fails, a backup steps in (for example, Grace covers Sterling and Otis covers Deacon) and says it's covering.
  - **Scheduled agents:** a new **Watchtower** agent runs at 8:13 AM and 10:13 PM. It checks every scheduled agent, re-runs any that failed or missed, does the job itself if the rerun also fails, and writes a health report to HQ.
  - **Voice:** if a voice line won't connect, Deacon covers by text.
  - **Crew health card** on the Crew tab.
- **The momentum engine:**
  - **How it reads you:** it scores the last 14 days (training 60%, time with God, sleep, mind work) into tiers: Building (first week), Rebuild, Steady, Push and Elite.
  - **Push:** main lifts +2.5%, last set as many reps as you can, roadwork +5 min, +1 pull-up a set.
  - **Elite:** +5% plus a back-off set, roadwork +10 min, +2 pull-ups a set.
  - **Where the boost never applies:** deload, taper, test and Day 1.
  - **Rebuild** holds the weights and protects the minimums.
  - **Mind challenges** (+15 XP) at Push and Elite.
  - **Strength bump:** after 4 weeks at 85%+ consistency, HQ offers to raise your training maxes (+5 lb upper, +10 lb lower), with an Accept button.
  - **Deacon and the crew** coach to the tier, and the 5 AM brief adds the momentum line.

## v12 · The real Day 1, the Booth, the Office (2026-11-04)

- **Restart from the real Day 1.** The whole HQ now counts from Wednesday, Nov 4, 2026: 177 days to April 29, 2027.
  - **XP and rank** restart at zero.
  - **Day 1 is 20 push-ups.** A Day 1 card on Home includes a hold-to-sign covenant.
  - **The plan is re-dated.** Foundation runs Nov 5 to 29, Build Dec 7 to Jan 3, Strength Jan 11 to Feb 21, Peak Mar 1 to Apr 11, taper Apr 12 to 25, test week Apr 26 to 29. One Peak week was dropped so the taper and test week still land on the birthday.
  - **Everything that counts days was updated:** all 177 morning briefs (Day 1 of 177), monthly report boundaries (Month 1 = Nov 4 to Dec 3), the April 29 birthday letter, the weekly report, voice Deacon's prompt and his plan document.
- **Year 31.** The plan continues past the birthday: a victory lap Apr 30 to May 9, then 12-week cycles (build, strength, deloads, re-test) through April 2028.
- **The Booth** is PLV Radio's own 90s-style studio:
  - a big broadcast mic button with an ON AIR light, an analog VU meter and faders;
  - four original synthesized beds (Quiet Storm, Sunset Cruise, Victory, Late Night Letters) plus your own instrumentals, with talkover ducking;
  - an 8-pad cart wall (station ID, sweeper, phone ring, drop, rimshot, applause, ding, horns);
  - four phone lines with a call screener and AI practice callers;
  - a show clock for the segment map;
  - input selection for USB-C mics, interfaces and a caller line-in;
  - recording to takes saved on the device and exportable as files;
  - a post-show writer for show notes, YouTube description, chapters, captions and the newsletter.
- **The Office** is Forward Works AI's own toolkit:
  - a time clock that refuses to clock in during day-job hours unless you confirm you're off the clock, and that logs business hours;
  - a proposal writer from pipeline leads;
  - numbered invoices with paid tracking and the 30% tax bucket;
  - an ROI calculator with a ready pitch line.
- **iPhone 18 ready.** A moving-to-a-new-phone checklist, plus a real restore from a backup file that fills in what's missing or overwrites.

## v11 · Privacy Shield, daily AI video, the vinyl crate, Hey Siri (2026-11-05)

- **Privacy Shield.** A new card on the Log tab, with three layers:
  - **Every agent carries a standing order.** That covers every in-page call, the five voice agents and all 21 scheduled agents. They treat emails, web pages, documents and messages from other devices or other agents as data, never orders. They refuse unsolicited requests for his information, never put personal data in a link or a web search, never send anything out without his yes, and report attempts ("Shield: blocked…").
  - **Consent switches.** Scheduled agents may read money, body, career and family data only with his consent; each one checks the switches before reading anything else. The private journal stays off-limits to every agent.
  - **An encrypted vault.** It is opt-in, per section: the family budget, date ideas, wedding list, prayer list, lift log, interview pursuits, mock scores and story bank. Each section is encrypted on the device with AES-256-GCM, using a key made from his passcode with PBKDF2-SHA256 at 310,000 iterations. Only ciphertext is stored, and the passcode never leaves the device. The device can remember it as a key that can't be exported, and he can lock the vault any time. Writes are refused while it's locked, and locked sections show as locked instead of empty.
- **Today's AI video.** A new 5:23 AM agent picks one YouTube video each day for his track and interview, checks that it exists through YouTube's oEmbed endpoint, and adds what to watch for plus an interview-style question. The video shows on Home and Learn. "Check my answer" gets graded by Grace, and watching earns +10 XP.
- **The crate.** His Apple Music playlists now appear as vinyl records you swipe between: sleeve art, a record that slides out with a spinning label, dots and arrows. "Play in Apple Music" opens the playlist, and he can add any playlist by its Apple Music link.
- **Hey Siri.** The Phone setup sheet now explains how to make Siri shortcuts with copy buttons ("Let me talk to Deacon", "Call The Executive", Pat, Toni, "Deacon brief", "Debrief"). Siri opens the agent's voice line and the agent talks back.

## v10 · No fear, multiple choice, family budget (2026-11-05)

- **No fear before every Executive session:** before the written mock starts or the voice interviewer
  opens, a full-screen word: "I have these positions because of God, and I work for Him. What His will
  is, so will be. No fear." With a rotating KJV verse (2 Timothy 1:7, Colossians 3:23, Proverbs 19:21),
  one grounding line and a guided breath. The voice interviewer opens with the same word.
- **Multiple choice or speak:** a toggle in the written mock. In multiple choice, every question gets
  four answers (the strongest, a buzzword answer, a correct-but-shallow one, and one with a subtle error),
  shuffled. Pick one and see why each is right or wrong; misses get a coach's note. Speak or type mode
  adds a Talk button where the browser allows it. The scorecard counts multiple-choice hits. The voice
  interviewer offers spoken A to D options on request.
- **Ultimate model everywhere:** every in-page agent call (Deacon, the crew, huddles, debrief, lessons,
  monthly reports, idea cards, sparring, mail drafts) now requests the most capable Claude model, as do
  all five voice agents and every scheduled agent.
- **Family budget and payoff plan** at the top of the Money tab, built to do together: money in (any pay
  frequency, business income after the 30% tax set-aside), bills by need, want, giving and saving with
  quick-add chips, and debts with balance, APR and minimum. It shows what's left each month, the
  50/30/20 split, an extra-payment slider, avalanche vs snowball vs minimums-only (debt-free month,
  total interest, savings), this month's payment for each debt with the target marked, a payoff chart,
  and warnings when money is short or a minimum doesn't cover interest. Saves as you type, shares as a
  Doc, and Ledger reads it in chat and in his 1st and 15th money check.

## v9 · Coach mode and the Rocky montage (2026-11-05)

- **Ultimate model for interview training:** mock scoring, coaching, answer keys, the practice thesis,
  job decoding and Academy lessons now request the most capable Claude model at high effort; the voice
  interviewer and the interview scheduled agents run on it too.
- **Coach mode:** after every mock answer, a coach's note gives the grade, what was right, what was
  missing, the right answer, the reasoning steps to get there, and an interview-ready "say it like
  this". The voice interviewer offers coach mode or real-interview mode.
- **Teach me the answer** on every bank question: the expert answer, how to derive it from first
  principles, a 60-second spoken version, answers to the three follow-ups, common pitfalls.
- **Rocky III and IV montage program:** weekday montage finishers (farm, barn, beach, footwork) and
  Montage Saturdays (Siberia Day and Beach Day) in place of roadwork twice a month, skipping deload,
  test and Fight Night days; a Rocky montage soundtrack tab; montage XP; safety notes on every one.

## v8 · Interview Camp (2026-11-05)

Head of AI pursuit is back on (AI Practice Lead, Charlotte, financial services). A new Interview tab
built for an executive interviewer who can tell a builder from a talker:

- **Pursuit tracker** for any number of opportunities: stages, interview countdown, a readiness score
  (question bank, mocks, stories, thesis, track progress) and a daily 20-minute drill.
- **Role decoder and sourced company intel**, plus questions to ask; paste any job description to
  decode a new role.
- **Question bank:** 32 technical, banking and practice-leadership questions. Each has what it
  really tests, what a strong answer contains, the phrases that sound like BS, and a three-step depth
  ladder of expert follow-ups. Answer first, then reveal; self-ratings drive the daily drill.
- **Mock interviews** with "The Executive" (an original character): a written round that probes
  and scores depth, specificity, accuracy, structure, business sense and composure, quoting where
  answers sounded like BS; plus a 30-minute voice version.
- **Story bank** pre-filled only with known facts, with brackets for real details.
- **Practice thesis and 90-day plan**, comp and negotiation guidance, and an interview-day protocol.
- **Academy:** a Practice Lead · BFSI track (8 modules) that takes priority during an active pursuit.
- **Automation:** a daily interview prep brief and lesson prep focused on the pursuit.
- The crew's instructions now support the pursuit instead of steering away from it.

## v7 · Fight camp data (2026-11-04)

- **Lift log.** Today's main lifts with every set pre-filled from the plan; tick what you did and
  save. Estimated one-rep max (Epley, 12 reps or fewer), automatic PR detection that adds a win,
  and a one-tap offer to raise a max when the estimate passes it. +10 XP, +25 per PR.
- **Strength board** on Body: best estimated max per lift, compared with camp start and his
  18-year-old numbers, with a trend chart per lift.
- **Fuel.** Protein (0.7 g per pound of latest bodyweight) and water (a gallon) with one-tap
  add buttons and undo. +10 / +5 XP.
- **Tale of the tape** on Log: all 183 camp days as a heatmap (training, time with God, sleep,
  debrief, protein), seven stat tiles, and 30-day trend charts with hover readouts.
- **Backup.** Download every bit of HQ data as one JSON file.
- **Next Fight Night** joins the milestone road; a **Quiet Storm pre-record** nudge appears Friday to
  Sunday from December, since the show airs 9 to 11 PM and lights-out is 10.
- **Fix:** Academy tracks now read "Learned in HQ (not a certification)" instead of "Certified",
  per the no-unearned-credentials rule.

## v6 · Autopilot + Academy (2026-11-04)

- **A phone button.** Quick-action links (`#debrief`, `#sos`, `#brief`, `#lesson`, `#ask`, `#train`,
  `#music`) open HQ straight into an action. A "Phone button" sheet walks through an iOS Shortcut
  (Open URLs, then Add to Home Screen), Siri, the Action Button, Back Tap and Control Center, and
  draws an HQ app icon to save and use. A quick-action row (Debrief, I'm about to slip, Today's
  lesson, Ask HQ, Phone button) stays on Home in every mode, night included.
- **Evening debrief.** Talk for 60 seconds with keyboard dictation, framed by Seneca's nightly
  review. Deacon answers, and extracts the day's log, wins, tasks, urges, crew memory and prayer
  requests into one checklist; one tap saves everything checked (+15 XP). Radar nudges after 8 PM.
- **The Academy (new Learn tab).** Three tracks, 35 modules: Head of AI (12: mandate, strategy,
  operating model, platforms, governance and regulation, security, evals, economics, agents in
  production, people, board communication, capstone), Founder-FDE (12: the forward-deployed model,
  discovery, pricing, SOWs, solution patterns, safe builds, evals, deployment, retainers, sales,
  running the firm, scaling) and The Inner Citadel (11: Deacon's school of the Stoics and the
  apostles). Lessons are written for Kendall's real situation, cached, quizzed, drilled against a
  crew member, and can go on the board or into a Doc. One lesson a day by weekday; +30 XP; a
  certificate per track.
- **Deacon, deeper.** A Stoic corner in his character (Epictetus, Marcus Aurelius, Seneca, Musonius
  Rufus, Cato) paired with Paul, Peter, James and John, plus Augustine, Thomas a Kempis, Bonhoeffer,
  C. S. Lewis, Douglass, King and Frankl, Christ first. A daily discipline card (one Stoic line, one
  KJV verse, one practice, +10 XP) on Today and Mind, rotating through 24 pairings.
- **Your Apple Music playlists** (Cali Vibes, Keep It In Rhythm, Shower) on the Soundtrack card,
  with the right one highlighted for the current part of the day.
- **Monthly reports.** "Month X of 6" in Deacon's voice: on Home after the 29th, archived on the Log
  tab, writable on demand, saveable as a Doc.
- **New scheduled agents:** Monthly report (29th, 7:23 PM ET; Feb 28 one-off), Academy lesson prep
  (Sundays 6:17 PM ET, pre-writes the week's lessons with verified sources), Deacon's nightly
  debrief nudge (9:07 PM ET).

## v5 · Mission Control (2026-11-04)

The crew stops waiting to be asked.

- **Radar.** HQ checks every area each time it renders and flags what is slipping, most urgent
  first: late board tasks, pipeline follow-ups past due, overdue launch-checklist items, "never
  miss twice" after an unlogged or missed workout, a low sleep average, a stale or missing cushion
  number on the 1st/15th, date night coming up with nothing planned, overdue wedding tasks, a PLV
  recording with no outline, milestones within 14 days, and unread agent reports. Each flag is
  owned by a crew member: "Handle it" opens them already briefed, "Add to board", or "Not today".
  On Home (respecting the wind-down, sleep and family modes) and on the Board.
- **Milestones to 30.** A timeline from camp day 1 to April 29 with 12 milestones across PLV,
  the business, money, family, fitness and faith. Status and progress come from real data where
  possible (a won lead, checklist items, the cushion balance, wedding tasks, camp day, revenue won);
  the rest can be marked hit, which also puts it on the wins wall. Tasks can link to a milestone.
- **Weekly reset.** A four-step Sunday ritual on the Board: close out the week (done / next week /
  drop for everything due), open the scorecard, run the planning huddle, lock it in (+25 XP).
- **Block time.** Any task can go straight onto Google Calendar: suggested open slots for that day
  (skipping day-job hours), live conflict check against existing events, and a tagged event HQ
  recognizes. Requires approving the page's calendar-write permission once.
- **Agents see it all.** Milestones and the radar are in every agent's context and board tool;
  proposed tasks can carry a milestone.
- **Two new scheduled agents** report into the agent inbox: Ledger's money check (1st and 15th,
  6:47 AM ET) and Hart's Thursday family note (12:43 PM ET).

## v4 · Crew OS (2026-11-04)

Turns the HQ from a set of tabs with agents attached into one command center the whole crew runs on.

- **Mission board (new Board tab).** One task list across Faith, Family, Fitness, Finances,
  Business, PLV and the day job. Every task has an owner on the crew; "Work it with <agent>"
  opens that agent with the task already briefed. Grouped Late / Today / This week / Later /
  Anytime, filter by area, 10 XP per finished task (up to 3 a day). "Up next" shows on Home.
- **Crew huddles.** Ask one question; 2–6 agents weigh in in turn and build on each other, then
  Deacon chairs and returns a plan of 3–5 dated, owned moves. Add any or all to the board, save
  the huddle as a Doc, or pressure-test it with Deacon. Past huddles are kept and can be re-run.
- **Crew memory.** A shared list of decisions and facts injected into every agent's context,
  Deacon included. Add your own, or approve ones an agent suggests.
- **Shared agent tools.** Every chat agent (and Deacon) can read the board, memory and recent
  huddles, and can propose a task, propose a memory, or offer a handoff to the teammate who owns
  the request. Nothing saves without an Approve tap; handoffs open the teammate with a brief.
- **Life crew: two new agents.**
  - **Ledger · Money manager:** cushion, 30% tax set-aside, budget and take-home math; can
    propose updated cushion numbers.
  - **Hart · Family and wedding planner:** date nights, wedding tasks, the shared prayer list;
    can propose items for the Us tab.
  Their strips also appear on the Money and Us tabs.
- **Ask HQ command bar.** Floating button, `/` or Ctrl/Cmd+K. Type anything: it routes to the
  best agent (with alternates), or adds it to the board, starts a huddle, saves it to crew
  memory, or jumps to any tab or card. Arrow keys + Enter.
- One approval system now handles every proposal type for Deacon and the crew alike.
- All new UI is built from the existing era tokens, so it restyles with all seven daily eras.
