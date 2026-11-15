# 00 — Foundations: What "Ghost" Actually Means

## The problem with "be a ghost"
"Ghost" is vague until you name the ghost's audience. Ghost to an advertiser,
ghost to your ISP, and ghost to a targeted attacker are three different goals
with three different price tags. Wanting all three at once is how beginners
buy a VPN and call it done.

## Your threat model (locked)
- ISP
- Advertisers / commercial trackers
- Opportunistic hackers
- **NOT** a targeted human adversary

That's a clean, achievable target with normal tools. No Tails, no burner
laptops, no drama.

## Definition used for the whole guide
> A ghost is someone whose cost to track exceeds the tracker's payoff.
> You are not invisible — you are unprofitable.

## What this implies
- Goal is not invisibility; it is **cost asymmetry**.
- Defenses layer: DNS → transport → browser → device.
- If a countermeasure makes tracking more expensive than the payoff, it works.
- If it only *feels* private (incognito mode, "free VPN"), it doesn't.
