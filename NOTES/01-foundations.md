work 1          # jumps into PRA/CTICALS/01-foundations
go              # back to master
## 1.1 How the Internet Works

### Core concepts
- Client = the one asking (me on my phone)
- Server = the one answering (Google's computer)
- IP address = number plate of every device (142.250.185.78)
- Domain name = human-friendly name (google.com)
- DNS = phonebook. You give name, it gives number.

### My matatu analogy
- Client = passenger asking
- Server = destination stage
- IP = matatu number plate
- DNS = conductor who tells you which matatu to board
- Data packets = parcels travelling different routes

### Practical commands I ran
- curl -I https://google.com  -> shows HTTP headers (server alive?)
- ping -c 3 google.com        -> tests if server replies + speed in ms
- nslookup google.com         -> asks DNS for the IP address

### What I learned
i learned ip address number assigned to every device
### Website IP vs Device IP

- Device IP = MY address (where data goes to/from me)
  Example: 192.168.1.5 (WiFi) or 41.90.xx.xx (mobile data)

- Website IP = the SERVER's address (where I fetch pages from)
  Example: 142.250.185.78 (Google)

- DNS = translates domain name -> website IP
  (Domain -> Number Service)

- Both needed: one to send, one to receive.
- NAT hides my private IP behind a public one.
### Git lesson learned
- "working tree clean" = everything is saved and committed
- Not an error. Means git has nothing new to do.
- Use `git log --oneline` to see recent commits
- My push script auto-stages everything (git add .)
  so files get committed even without running git add manually
### My own words (locked in)
- HTTP = rules computers follow to exchange data
- 200 = success
- 404 = not available / not found
- 301 = moved permanently (redirect)
### 1.4 — My own words
- ls       = list files
- ls -la   = list with all details + hidden + permissions + sizes
- |        = pipe: output of one command becomes input to another
- >        = overwrite (dangerous, use carefully)
- >>       = append (safer)
