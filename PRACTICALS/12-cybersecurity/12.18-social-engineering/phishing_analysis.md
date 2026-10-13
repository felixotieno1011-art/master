# 12.18 Social Engineering — Analysis

## Scenario
SMS claiming to be from Safaricom:
"Dear customer, this is Safaricom. Your M-Pesa account has been
flagged for suspicious activity. To avoid suspension, dial
*106*123# and enter your PIN to verify. Act now — your line will
be blocked within 30 minutes. Call 0722000000 for help."

---

## 1. Type of attack
Smishing (SMS phishing) + Vishing (voice phishing fallback via the
fake phone number)

## 2. Emotion targeted
- FEAR — "flagged for suspicious activity"
- URGENCY — "act now", "30 minutes"
- THREAT — "your line will be blocked"

## 3. Red flags
1. Asks for PIN — Safaricom NEVER asks for your PIN. No real company does.
2. Weird USSD code (*106*123#) — real M-Pesa code is *334#
3. Fake urgency — 30 minutes to act is designed to panic you
4. "Dear customer" — generic, real messages use your name
5. Fake help number (0722000000) — belongs to the scammer
6. Threat of suspension — real companies inform, they don't threaten

## 4. What a safe version looks like
- Never asks for PIN or password
- Points to official channels (M-Pesa app, *334#, real agent)
- Uses your actual name
- No threats, no urgency
- Official customer care = 100, not random 07xx numbers

## My own words (locked in)
- Safaricom never hurries someone — urgency = scam
- Fear + urgency is the classic one-two punch of social engineering
- The target is not the system — it's the human holding the PIN
