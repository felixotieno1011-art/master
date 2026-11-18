# 12 — Ghost Box: Lab Notes & Field Tests

## Part A: The Tor Experiment (Your Research)
- **Test 1 (Circuit 1):** IP changed to `185.220.101.170`. (Site saw Tor exit).
- **Test 2 (Restart):** New IP `185.231.101.53`. (New circuit).
- **Test 3 (Persistence):** Same IP for ~10 mins. (Tor keeps a circuit open per site).
- **Test 4 (No Tor):** Real IP visible. (Confirmed baseline leak).

## Part B: The Tool Comparison
| Tool | Hides from Site? | Hides from ISP? | Who is the weak link? |
| :--- | :--- | :--- | :--- |
| **VPN** | Yes | Yes (encrypted tunnel) | The VPN provider (they see your real IP). |
| **Tor** | Yes | Yes (encrypted) | None (3 hops, no single point of failure). |
| **I2P** | Yes (internal) | Yes | Very slow, hard to browse normal sites. |
| **Proxy** | Yes | No (usually) | The proxy owner (single hop). |

## Part C: The Combo Experiments
1. **Safaricom -> VPN -> Tor -> Website**
   - *Pro:* ISP doesn't know you use Tor.
   - *Con:* VPN provider knows your real IP and that you use Tor.
   - *Verdict:* Better for hiding Tor, but requires trusting the VPN.
2. **Tor -> VPN -> Website**
   - *Pro:* Fewer sites block you (VPN IP is clean).
   - *Con:* VPN sees your traffic. Paying for it leaves a trace.
   - *Verdict:* Faster, but not perfectly anonymous.

## Part D: What Breaks the Ghost (OpSec)
- Logging into a real account inside Tor (links Ghost IP to real name).
- Downloading a file in Tor and opening it outside Tor (leaks real IP).
- Sharing emails, photos, or writing styles between Real and Ghost.

## Conclusion
Perfect anonymity does not exist. It depends on keeping Real World and Ghost World separate at all times. Tor hides the connection; only OpSec hides the human.
