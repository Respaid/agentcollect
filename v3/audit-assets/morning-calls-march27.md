# Mystery Shopper Calls — March 27, 2026

## Summary

- **5 AM PDT batch (12:02 UTC):** All calls hit closed/voicemail. No data — all prospects were before business hours.
- **7 AM PDT batch (14:02 UTC):** 8 calls placed across 5 prospects + 1 collection agency. 1 human reached (Texas Disposal). 1 voicemail left (Prudential AR direct). Rest: IVR dead-ends.
- **Verliance call (14:15 UTC):** Human answered at collection agency. Engaged in 2.5-minute conversation. Could not locate fictional account.

---

## Call Results Table

| # | Company | Number | Time (local) | Duration | Result | Human? | Recording |
|---|---------|--------|-------------|----------|--------|--------|-----------|
| 1 | Prudential Overall | +1 (949) 250-4855 (AR direct) | 7:02 AM PDT | 32s | Voicemail — left message as "Mike from Summit Auto Repair" | No | [recording](https://dxc03zgurdly9.cloudfront.net/b909b9caf166a77e2ef4c536e92b279b0a35af42d60b1e1a760c5a59e2b5f7d4/recording.wav) |
| 2 | Prudential Overall | +1 (800) 767-5536 (main) | 7:02 AM PDT | 19s | Closed — "We are currently closed" | No | [recording](https://dxc03zgurdly9.cloudfront.net/688a481b4c8a4db88d74aadd16eb4dd07ffd99182712329b27a5fb58ba92c870/recording.wav) |
| 3 | Texas Disposal Systems | +1 (800) 375-8375 | 9:02 AM CDT | 72s | **HUMAN ANSWERED** — "How may I help you? Texas Disposal." | **YES (64s)** | [recording](https://dxc03zgurdly9.cloudfront.net/67838f19b3c59c80364f205a186d5bf8f41177c3f262eb709d2ac6195bb90027/recording.wav) |
| 4 | Kimble Companies | +1 (330) 343-1226 (secondary) | 10:02 AM EDT | 67s | IVR > operator transfer > no answer > agent gave up | No | [recording](https://dxc03zgurdly9.cloudfront.net/57bd7c389aeb6ac18595ece5261e29322f160bf12fa33b1b38f4c428ee2563af/recording.wav) |
| 5 | Kimble Companies | +1 (800) 201-0005 (main) | 10:02 AM EDT | 71s | IVR > operator transfer > no answer > agent gave up | No | [recording](https://dxc03zgurdly9.cloudfront.net/5ec2ca6dc96ae968d569bcee65473f059497960818299083de3c884f94ac5670/recording.wav) |
| 6 | Automation Personnel | +1 (205) 733-3700 | 9:02 AM CDT | 10s | IVR answered then **disconnected caller in 10s** | No | [recording](https://dxc03zgurdly9.cloudfront.net/7527731fed31752266de6df8c17bcf300e1e1341a3a38d474b3206181034b41b/recording.wav) |
| 7 | Qualified Staffing | +1 (810) 230-0368 | 10:02 AM EDT | 96s | IVR (press 7 for AR) > voicemail — "unable to take your call" | No | [recording](https://dxc03zgurdly9.cloudfront.net/10be442931e6ab3a69ef45eb1be03aed3c9be48d677b6fa6cbd96a74c5d4ed52/recording.wav) |
| 8 | **Verliance Inc** (collection agency) | +1 (877) 643-4549 | 10:15 AM EDT | 148s | **HUMAN ANSWERED** — operator "Good Lions." Engaged in conversation, asked for file number, address. | **YES (~38s)** | [recording](https://dxc03zgurdly9.cloudfront.net/214fff4da0d4b7f2d47f7afc89d17bdbb8b251be0ea6c412656fc3a02cba8836/recording.wav) |

---

## Key Findings Per Company

### Prudential Overall Supply (Grade: PENDING)
- **AR direct line** (+19492504855): Closed at 7 AM PDT. Mystery shopper left voicemail as "Mike from Summit Auto Repair" requesting callback about a $450 drain cleaning bill. Callback number: (949) 741-7328.
- **Main 800 line** (+18007675536): Also closed at 7 AM PDT.
- **Action needed:** Retry both lines between 9 AM-12 PM PDT. Monitor (949) 741-7328 for callback from the voicemail — callback response time is a key audit metric.
- **Audit page data:** Voicemail left, awaiting callback timing.

### Texas Disposal Systems (Grade: A)
- **Best performer.** Human answered in ~64 seconds at 9:02 AM CDT.
- IVR has payment option (press 3) and operator option (press 0). Agent pressed 0 and reached a live person.
- Operator said "How may I help you? Texas Disposal. May I help you?" — waited for response, agent did not engage further (call ended by user_hangup, likely because timing agent has no conversation persona).
- **Audit page data:** Live billing contact reachable. 64s time-to-human. IVR includes self-serve payment option.
- **Email copy angle:** "Called (800) 375-8375 this morning. Someone answered in 64 seconds. That's good. But what happens after hours?"

### Kimble Companies (Grade: D)
- **Two numbers, same IVR, zero humans.**
- Both +18002010005 (main) and +13303431226 (secondary) route to identical IVR: refuse/limestone/coal/oil/gas menu + operator (press 0).
- Both times: operator transfer initiated, nobody picked up. Agent waited ~20s on hold then gave up.
- No dedicated AR option in IVR.
- **Audit page data:** Both numbers confirmed as dead ends at 10 AM EDT. No AR IVR option. Operator unanswered.
- **Email copy angle:** "Called both numbers. Same system. Pressed 0 for operator. No answer at 10 AM."

### Automation Personnel (Grade: F)
- **Worst performer.** IVR answered "Thank you for choosing Automation Personnel" then disconnected the call after 10 seconds (user_hangup).
- Possible auto-screening for unknown/VoIP caller IDs.
- **Audit page data:** IVR disconnects callers. Effectively unreachable by phone.
- **Action needed:** Retry — could be caller screening on the Telnyx number. Try with a different CallerID.
- **Email copy angle:** "Called (205) 733-3700. Your system hung up on me in 10 seconds."

### Qualified Staffing (Grade: C)
- IVR has a dedicated AR option (press 7 for accounts receivable), which is notable.
- However, pressing 7 routes to general voicemail — "We are unable to take your call at this time" — at 10:02 AM EDT.
- Also has: benefits, workers comp, unemployment, FMLA, payroll, AP, AR, and sales departments listed in IVR.
- Employment verification requires fax to (810) 230-8057.
- **Audit page data:** AR listed in IVR but voicemail-only at business hours. Structured IVR with 8 department options.
- **Email copy angle:** "Pressed 7 for accounts receivable. Voicemail at 10 AM."

### Verliance Inc — Collection Agency (NEW)
- **Human answered in ~38 seconds.** Operator identified as "Good Lions" (Verliance subsidiary/brand).
- Mystery shopper posed as "Mike from Summit Auto Repair" with an outstanding balance wanting to pay.
- Operator asked for file number (agent didn't have one), tried phone lookup (didn't work), asked for business name ("Summit Auto Repair"), then asked for address (agent didn't have it).
- Operator concluded: "We would need more information. You can give us a callback later."
- **Key intel:** Verliance uses file numbers for account lookup. Name + phone search didn't find the fictional account. They are professional and polite.
- **Audit page data:** Collection agency with live operators during business hours. Uses file-number-based lookup system. ~38s to reach a human.

---

## Scorecard Summary

| Company | Grade | Key Finding |
|---------|-------|-------------|
| Texas Disposal Systems | **A** | Live human in 64s. Payment IVR. Phones staffed at 9 AM CDT. |
| Qualified Staffing | **C** | AR option in IVR but hits voicemail at 10 AM EDT. |
| Kimble Companies | **D** | Both numbers same IVR. Operator transfer. No answer at 10 AM EDT. |
| Automation Personnel | **F** | IVR disconnects in 10 seconds. Unreachable. |
| Prudential Overall | **PENDING** | Called at 7 AM PDT before hours. Retry + monitoring voicemail callback. |
| Verliance Inc | **B+** | Live human in 38s. Professional. File-number lookup system. |

---

## Follow-Up Actions

1. **Prudential Overall:** Retry both numbers between 9 AM-12 PM PDT today (16:00-19:00 UTC)
2. **Prudential AR callback:** Monitor +19497417328 for incoming call from (949) 250-4855 — measure callback response time
3. **Automation Personnel:** Retry with different CallerID — possible VoIP screening
4. **Verliance:** Consider second call with more complete fictional data (address, file number) to test deeper into their process
5. **Texas Disposal:** Consider mystery shopper call (not just timing) to test full billing conversation

---

## Call IDs Reference

| Call ID | Company | Agent |
|---------|---------|-------|
| `call_0e7c4afa52879f4eb9d5f4b949a` | Prudential AR direct | Mystery Shopper |
| `call_16eb9e52f2f239e2780d9823473` | Prudential main | Timing |
| `call_c1c6bcda83f7552922e4bddb93a` | Texas Disposal | Timing |
| `call_f3b21331bbe444650db24a396e4` | Kimble secondary | Timing |
| `call_d93b02667834f083b1d7a959f9f` | Kimble main | Timing |
| `call_7451272fbadd39f4e2ce2276371` | Automation Personnel | Timing |
| `call_13f09ae0d51872af341ee578510` | Qualified Staffing | Timing |
| `call_3a0d027ad3ab28918c4d209a473` | Verliance Inc | Mystery Shopper |
