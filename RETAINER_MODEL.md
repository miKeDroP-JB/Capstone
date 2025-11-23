# 💵 RETAINER MODEL - $500 Upfront, Fully Refundable

**New Business Model:** Small retainer + revenue share

---

## 📋 THE OFFER

### What Clients Pay:

**Upfront:**
- $500 retainer (covers your $10-20k upfront investment in data/research/dev)

**Ongoing:**
- 20% of new revenue generated (you keep 20%, they keep 80%)

### The Guarantee:

**If we don't make them money in 90 days, they get the $500 back.**
- Full refund
- No questions asked
- They risk literally nothing

---

## 🎯 WHY THIS WORKS

### Filters Serious Clients:
- $500 is enough to ensure commitment
- But low enough that anyone serious will pay it
- Eliminates tire-kickers

### Covers Your Costs:
- You invest $10-20k per client (data, research, dev, setup)
- $500 retainer covers initial costs
- Revenue share covers ongoing

### Zero Risk for Client:
- Fully refundable if no results
- Only ongoing cost is revenue share (which means they're making money)
- Literally cannot lose

### Profitable for You:
- $500 × 30 closes = $15,000 immediate cash
- Plus 20% ongoing revenue share
- Plus refund rate will be low (because you deliver results)

---

## 📞 THE NEW PITCH

### Opening (Same):
```
"Hi, this is [YOUR NAME]. I help HVAC companies like yours get 20-30%
more customers using AI automation. Got 60 seconds?"
```

### Discovery (Same):
```
"What's your biggest challenge with getting new customers?"
"How are you currently handling bookings?"
"What takes most of your time?"
```

### Pitch (UPDATED WITH RETAINER):
```
"Perfect! I can build you a [SOLUTION] in about [TIME].

Here's the deal - normally this costs $3,000-5,000, but I have
a better model:

There's a small $500 retainer to get started. This covers my upfront
costs - I invest $10-20k in data, research, and development for your
custom solution.

Here's the best part: If I don't make you money in the first 90 days,
you get the $500 back. Full refund. You risk nothing.

After that, I get 20% of what it makes you. You keep 80%.

So if this helps you make an extra $10,000, you keep $8,000 and
I get $2,000.

You're only out $500 to start, fully refundable if no results. Fair?"
```

### Close (UPDATED):
```
"Great! Here's what happens next:

1. You pay the $500 retainer - I'll send you a Stripe payment link,
   takes 30 seconds
2. I start building your solution immediately
3. You review it and we tweak it
4. You start using it and making money
5. If no results in 90 days, you get the $500 back
6. After that, we share revenue: you keep 80%, I get 20%

I can send you the payment link right now and start building today.
Want to do this?"
```

---

## 💳 COLLECTING THE RETAINER

### Step 1: Client Agrees

When they say yes:
```
"Awesome! What's your email address? I'll send you the Stripe payment
link right now."
```

### Step 2: Create Payment Link

```bash
python stripe_retainer.py --create "Company Name" --email client@email.com
```

This shows you:
1. How to create the Stripe payment link
2. What to send the client
3. Payment tracking ID

### Step 3: Send Link to Client

```
"I just sent you an email with the payment link. It's $500 - takes
30 seconds to pay. Once it goes through, I'll start building
immediately. Usually takes [TIME] to complete."
```

### Step 4: Mark as Paid

When payment comes through:
```bash
python stripe_retainer.py --mark-paid ret_XXXXXX
```

### Step 5: Start Building

Now onboard them and deliver the solution!

---

## 💸 REFUND POLICY

### When to Refund:

**90-day results check:**
- If client hasn't generated new revenue by day 90
- Process full $500 refund
- No questions asked

### How to Process Refund:

```bash
# Check if eligible
python stripe_retainer.py --check "Company Name"

# Process refund
python stripe_retainer.py --refund ret_XXXXXX
```

Then in Stripe:
1. Find the payment
2. Click "Refund"
3. Refund full $500

### Expected Refund Rate:

**Conservative:** 10% (you deliver results for 90%)
**Realistic:** 5% (you deliver results for 95%)
**Optimistic:** 0% (you deliver for everyone)

Even at 10% refund rate:
- 30 clients × $500 = $15,000 collected
- 3 refunds × $500 = -$1,500
- Net: $13,500 immediate cash

Plus ongoing 20% revenue share!

---

## 📊 REVENUE MODEL WITH RETAINER

### Example: 30 Closes

**Retainer Revenue:**
- 30 clients × $500 = $15,000
- 3 refunds (10%) = -$1,500
- Net retainers: $13,500

**Ongoing Revenue Share:**
- 30 clients × $10,000/month avg = $300,000/month
- Your 20% cut = $60,000/month
- Annual: $720,000

**Total First Month:**
- Retainers: $13,500
- Revenue share: $60,000
- Total: $73,500

**Total First Year:**
- Retainers: $13,500 (one-time)
- Revenue share: $720,000
- Total: $733,500

---

## 🎯 HANDLING OBJECTIONS

### "$ 500 is too much"

```
"I totally understand. Here's the thing - I'm investing $10-20k upfront
in data, research, and building your custom solution. The $500 just
covers my initial costs.

Plus, it's fully refundable if I don't make you money in 90 days.
So your actual risk is zero. You're just holding a spot."
```

### "Why do you need money upfront if you're so confident?"

```
"Great question! I AM confident - that's why I offer the 90-day
money-back guarantee. The $500 just ensures we're both serious.

I invest $10-20k per client in custom development. I need to know
you're committed before I make that investment. If I don't deliver
results, you get it back. Fair?"
```

### "Can I pay the $500 out of my first revenue?"

```
"I wish I could do that, but I have real upfront costs - servers,
data subscriptions, development time. The $500 covers those initial
expenses.

But remember: fully refundable if no results in 90 days. You literally
cannot lose."
```

### "I need to think about it"

```
"Totally fair. What specifically are you unsure about?

[Listen to concern]

How about this - let me email you the details. If you like it, we
move forward. If not, no worries. Sound good?"
```

---

## 📈 RETAINER DASHBOARD

### Check Status:

```bash
python stripe_retainer.py --dashboard
```

Shows:
- Total retainers collected
- Total refunded
- Net revenue
- Pending payments
- Refund-eligible clients

---

## ⚡ QUICK START WITH RETAINER

### Make a Call:

1. Use regular scripts
2. When they agree, collect email
3. Create payment link
4. Send link
5. Wait for payment
6. Mark as paid
7. Start building!

### Track Everything:

```bash
# Create payment link
python stripe_retainer.py --create "ABC HVAC" --email owner@abchvac.com

# Mark as paid when money hits Stripe
python stripe_retainer.py --mark-paid ret_20231123120000

# Check dashboard
python stripe_retainer.py --dashboard
```

---

## 💰 EXPECTED RESULTS (30 Calls)

### With 30% Close Rate (9 closes):

**Immediate (Retainers):**
- 9 × $500 = $4,500
- 1 refund (10%) = -$500
- Net: $4,000 immediate cash

**Monthly (Revenue Share):**
- 9 clients × $10,000 avg = $90,000/month
- Your 20% = $18,000/month
- Annual: $216,000

**Total First Year:**
- Retainers: $4,000
- Revenue share: $216,000
- Total: $220,000

### With 50 Closes:

**Immediate:**
- 50 × $500 = $25,000
- 5 refunds = -$2,500
- Net: $22,500

**Monthly:**
- 50 clients × $10,000 = $500,000/month
- Your 20% = $100,000/month
- Annual: $1,200,000

**Total First Year:** $1,222,500

---

## 🚀 SUMMARY

**The New Model:**
- $500 retainer (refundable if no results in 90 days)
- 20% ongoing revenue share (they keep 80%)

**Why It Works:**
- Filters serious clients
- Covers your $10-20k upfront investment
- Zero risk for client (fully refundable)
- Profitable for you (immediate + ongoing)

**How to Use:**
```bash
# Create payment link when you close
python stripe_retainer.py --create "Company" --email email@company.com

# Mark paid when money hits
python stripe_retainer.py --mark-paid ret_XXXXX

# Track revenue
python stripe_retainer.py --dashboard
```

**Expected Refund Rate:** 5-10% (because you deliver results)

**Expected Revenue:**
- Immediate: $500 × closes × 90% = cash today
- Ongoing: 20% of all client revenue = $10-30k/month per client

---

**Love • Loyalty • Honor • Everybody Eats** 💝

**Now with RETAINERS!** 💵
