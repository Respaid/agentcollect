# Roto-Rooter Billing & Payment Infrastructure Audit

**Date:** March 26, 2026
**Prepared for:** AgentCollect test audit page (agentcollect.com/audit/test-roto-rooter)
**Company:** Roto-Rooter (subsidiary of Chemed Corporation, NYSE: CHE)

---

## 1. Payment Portal Analysis

### Homepage to Payment: How Many Clicks?

**Answer: There is NO path from the homepage to bill pay.**

The rotorooter.com homepage contains zero billing or payment links. The navigation offers: Locations, Plumbing, Drains, Commercial, Water Quality, Water Damage, Coupons. The Contact Us page has four sections: For Service, Locations, Service Feedback, Careers -- no billing section.

A customer who wants to pay their bill must:
1. Already know the separate portal URL (rotorooter.spectrumretailnet.com) -- OR
2. Already have a Synchrony credit card account and log in at synchrony.com -- OR
3. Call 800-768-6911 and pay over the phone -- OR
4. Use a third-party service like doxo.com (which charges fees)

**Clicks from homepage to payment: IMPOSSIBLE** (no link exists)

### Payment Portal Assessment

**URL:** https://rotorooter.spectrumretailnet.com/PP?PAGE=AUTHENTICATE
**Powered by:** Tempus Technologies, Inc. (third-party vendor)
**Design age:** Appears circa 2005-2010. Dark blue background, basic HTML form, no modern UI.

Critical UX failures:
- Hosted on a completely different domain (spectrumretailnet.com) -- looks like a phishing site to customers
- No "Forgot Password" link
- No self-registration / "New User" option visible
- No mention of accepted payment methods
- No mobile-responsive design
- Requires pre-existing username/password with no clear way to obtain them
- "Returning User" implies you must have been set up by Roto-Rooter staff first

### Online Payment Options

| Method | Available? | Notes |
|--------|-----------|-------|
| Pay on rotorooter.com | NO | No billing section exists on the website |
| Payment portal (Tempus) | YES (hidden) | Separate domain, requires pre-existing account |
| Synchrony credit card | YES | For financing only, managed by Synchrony |
| Pay via app | NO | App is for scheduling/tracking only, no bill pay |
| Pay via doxo.com | YES | Third-party, charges processing fees |
| Pay by phone | YES | Call 800-768-6911 |
| Pay by mail | YES | Mail check to local office |

### Mobile App

- Available on iOS (App Store) and Android (Google Play)
- Features: scheduling, service tracking, appointment management, coupons
- Does NOT include bill pay or invoice viewing
- No customer account/portal for viewing past invoices

---

## 2. Billing Research

### Payment Methods Accepted
- Credit cards (Visa, MC, Amex, Discover)
- Debit cards
- Cash / check (in-person or mail)
- Synchrony financing credit card (26.99% APR, $29 activation fee)
- Financing plans: 0% for 6 months, 0% for 18 months, or 10.99% APR fixed

### Synchrony Financing Partnership
- Partnership since ~2013 (expanded in 2023)
- Private label credit card
- Technicians offer financing in-home via digital sales tool
- Plans: 6-month no interest, 18-month no interest, reduced APR options
- Account managed entirely through Synchrony's platform, not Roto-Rooter

### BBB Profile
- **Rating varies by location** -- franchise model means inconsistent BBB presence
- Corporate (Cincinnati, OH): Listed but rating varies
- Some locations: A+ BBB accredited (e.g., Greenville, SC since 2015)
- Some locations: Not BBB accredited (e.g., Irvine, CA)
- **60 complaints** with failure to respond noted
- Common complaint themes: hidden flat rates ($616/drain not disclosed upfront), aggressive upselling via free video inspections, billing without itemized receipts

### Review Ratings Summary

| Platform | Rating | Reviews |
|----------|--------|---------|
| Trustpilot | 1.7/5 ("Bad") | ~188 reviews |
| PissedConsumer | 1.5/5 | ~706 reviews |
| ConsumerAffairs | 2.1/5 | Multiple reviews |
| Glassdoor (employee) | 3.2/5 | ~985 reviews |
| BBB | Mixed by location | 60+ complaints |

### Key Billing Complaints from Customers
1. **Overbilling:** Customers report being overbilled multiple times, with errors only corrected when caught by the customer
2. **No itemized receipts:** Only a final price given, no parts/labor breakdown
3. **Aggressive collections:** Managers described as rude and unprofessional; accounts sent to collections over billing disputes
4. **Harassment:** One documented case of 17 ignored communications followed by legal threats and phone harassment
5. **Price gouging:** $1,000+ for 50-minute jobs, $1,893.67 for basic drain service
6. **Scheduling failures:** Text confirmations requiring response within 1 minute or service is cancelled

### Employee Reviews (Glassdoor/Indeed) on AR/Collections
- Collections and AR managers described as not on the same page as employees
- Employees not properly trained on billing procedures
- Morale and integrity at the bottom of priorities
- Management described as very unprofessional
- 49% would recommend working there; 47% positive outlook

---

## 3. Revenue & Cost Estimates

### Revenue
- **2024 Full Year Revenue:** ~$900M (estimated from quarterly reports)
  - Q1 2024: $235.2M
  - Q2 2024: $221.3M
  - Q3 2024: ~$214M
  - Q4 2024: $229.0M
- **2024 YoY change:** -5.2% decline
- **2025 guidance:** +2.4% to +3.0% growth
- **2026 guidance:** +3.0% to +3.5% growth (transition year)
- Parent company: Chemed Corporation (NYSE: CHE), total revenue $2.43B (2024)
- Roto-Rooter is the largest plumbing and drain cleaning company in North America

### Bad Debt Estimate

| Metric | Conservative (2%) | Moderate (3.5%) | Industry High (5%) |
|--------|-------------------|-----------------|---------------------|
| Revenue base | $900M | $900M | $900M |
| Estimated bad debt | $18M | $31.5M | $45M |
| At 30% recovery rate | $5.4M recoverable | $9.5M recoverable | $13.5M recoverable |

**Industry context:**
- General B2B bad debt rate: ~9% of all B2B sales (Dun & Bradstreet)
- Allowance for doubtful accounts: 1-5% of AR depending on industry
- Plumbing industry operates on ~22% gross margins, ~3% EBITDA -- making bad debt particularly painful
- 56% of small businesses report being affected by unpaid invoices
- Home services typically have higher bad debt than average due to residential customer mix and emergency service billing

### Estimated AR at Risk
Based on $900M revenue with typical home services AR cycle:
- **30-day AR outstanding:** ~$75M (1 month of revenue)
- **Estimated 60+ days past due:** ~$15-25M
- **Estimated write-offs per year:** $18-45M (2-5% of revenue)
- **Annual collection cost (in-house):** Estimated $3-5M (staff, systems, legal)

---

## 4. Competitor Comparison

### Roto-Rooter vs. Mr. Rooter (Neighborly) vs. ARS/Rescue Rooter

| Feature | Roto-Rooter | Mr. Rooter (Neighborly) | ARS/Rescue Rooter |
|---------|-------------|------------------------|-------------------|
| **Online bill pay on website** | NO (hidden portal on different domain) | NO clear portal | NO clear portal |
| **Customer portal** | Outdated Tempus portal (separate domain) | Neighborly App (service-focused) | None found |
| **Mobile app** | Yes (scheduling only, no bill pay) | Neighborly App (multi-brand) | No dedicated app |
| **Financing** | Synchrony (26.99% APR) | Financing partner (details vary) | Financing options available |
| **Payment methods** | CC, debit, cash, check, Synchrony | CC, debit, cash, check | CC, debit, cash, check |
| **Upfront pricing** | Flat-rate (not disclosed until on-site) | Upfront pricing commitment | Varies by location |
| **Revenue** | ~$900M | Part of Neighborly ($3.5B+ system) | Part of ARS (~$1.5B+) |
| **BBB presence** | Inconsistent (franchise model) | Generally accredited | Varies |
| **Trustpilot** | 1.7/5 | N/A | N/A |

### Key Differentiators (Opportunities for AgentCollect)

**What Roto-Rooter lacks that modern customers expect:**
1. No self-service bill pay on their main website
2. No invoice viewing or download capability online
3. No automated payment reminders (email/SMS)
4. No installment plan management portal
5. No dispute resolution portal
6. Payment portal looks like a phishing site (different domain, 2005 design)
7. No integration between their app and billing
8. No automated collections -- relies on manual calls and threatening letters

**The entire plumbing/home services industry has this problem.** None of the major players (Roto-Rooter, Mr. Rooter, ARS) have modern billing infrastructure. This is a massive whitespace for AgentCollect.

---

## 5. Screenshots Inventory

| Screenshot | File | Description |
|-----------|------|-------------|
| Homepage Desktop | `homepage-desktop-1440.png` | Main page at 1440px -- no billing links visible |
| Homepage Mobile | `homepage-mobile-375.png` | Mobile view at 375px -- no billing links |
| Payment Portal | `payment-portal-desktop-1440.png` | Hidden Tempus portal -- outdated 2005-era design |
| Financing Page | `financing-page-desktop-1440.png` | Synchrony financing promo page |
| Contact Us Page | `contact-us-desktop-1440.png` | Contact page with 4 sections, zero billing |

---

## 6. Audit Summary for Test Page

### Grade: D- (Billing Infrastructure)

**The good:**
- Major brand recognition (90+ years)
- 24/7 service availability
- Synchrony financing partnership
- Mobile app for scheduling

**The bad:**
- No bill pay link anywhere on their $900M company's website
- Payment portal hosted on a suspicious third-party domain
- Portal design is 20+ years old with no self-service registration
- No invoice viewing, no payment history, no automated reminders
- Customer complaints about billing errors, overbilling, aggressive collections
- 1.7/5 Trustpilot rating
- Franchise model creates inconsistent billing experiences

**The AgentCollect opportunity:**
- $900M revenue company with estimated $18-45M in annual bad debt
- Zero modern billing automation
- Customer experience around billing is actively hostile
- Competitors equally bad -- first mover in this vertical wins
- AI-powered collections could recover $5-13M annually that is currently written off
