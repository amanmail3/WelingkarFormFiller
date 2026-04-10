"""
Google Form Auto-Filler Bot
============================
Uses Playwright to intelligently detect and fill Google Form fields
with realistic Indian names, phone numbers, and emails.

Usage:
    python form_filler.py --url "https://forms.gle/..." --count 5
    python form_filler.py --url "https://forms.gle/..." --count 10 --headless
"""

import asyncio
import random
import argparse
import time
import re
import sys
from datetime import datetime, timedelta
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# ─────────────────────────────────────────────
#  INDIAN DATA GENERATORS
# ─────────────────────────────────────────────

FIRST_NAMES_MALE = [
    "Aarav", "Arjun", "Rohan", "Vivek", "Kiran", "Rahul", "Siddharth", "Aditya",
    "Vikram", "Nikhil", "Pranav", "Suresh", "Rajesh", "Amit", "Deepak", "Mohit",
    "Gaurav", "Harsh", "Ankit", "Akash", "Varun", "Kunal", "Kartik", "Yash",
    "Ishaan", "Dhruv", "Kabir", "Aryan", "Dev", "Ritesh", "Sachin", "Manish",
    "Vishal", "Tushar", "Piyush", "Abhishek", "Shivam", "Tarun", "Sandeep", "Ravi",
]

FIRST_NAMES_FEMALE = [
    "Ananya", "Priya", "Sneha", "Pooja", "Divya", "Riya", "Neha", "Kavya",
    "Shruti", "Ishita", "Tanvi", "Aditi", "Meera", "Sanya", "Aisha", "Nisha",
    "Komal", "Swati", "Ankita", "Simran", "Pallavi", "Deepika", "Ruchika", "Shreya",
    "Akansha", "Bhavna", "Chitra", "Disha", "Esha", "Falguni", "Gauri", "Heena",
    "Isha", "Jyoti", "Kritika", "Lakshmi", "Mansi", "Nupur", "Ojaswi", "Pari",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Joshi", "Mehta",
    "Shah", "Reddy", "Nair", "Iyer", "Pillai", "Menon", "Rao", "Mishra",
    "Tiwari", "Pandey", "Dubey", "Agarwal", "Bansal", "Chaudhary", "Malhotra",
    "Kapoor", "Bose", "Chatterjee", "Mukherjee", "Das", "Dutta", "Ghosh",
    "Desai", "Chauhan", "Yadav", "Maurya", "Saxena", "Rastogi", "Srivastava",
    "Tripathi", "Shukla", "Bajpai", "Kulkarni", "Patil", "Deshpande", "Jain",
]

EMAIL_DOMAINS = [
    "gmail.com", "yahoo.in", "hotmail.com", "outlook.com",
    "rediffmail.com", "ymail.com", "protonmail.com",
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
    "Ahmedabad", "Jaipur", "Lucknow", "Kochi", "Chandigarh", "Surat", "Indore",
    "Bhopal", "Patna", "Nagpur", "Vadodara", "Coimbatore", "Agra",
]

STATES = [
    "Maharashtra", "Karnataka", "Tamil Nadu", "Telangana", "Delhi", "Gujarat",
    "Rajasthan", "Uttar Pradesh", "West Bengal", "Kerala", "Punjab", "Haryana",
    "Madhya Pradesh", "Bihar", "Andhra Pradesh", "Odisha", "Assam", "Jharkhand",
]

COLLEGES = [
    "IIT Bombay", "IIT Delhi", "IIT Madras", "IIT Kanpur", "NIT Trichy",
    "BITS Pilani", "VIT Vellore", "SRM University", "Anna University",
    "Delhi University", "Mumbai University", "Pune University", "JNTU Hyderabad",
    "Jadavpur University", "Amity University", "Manipal University",
]

COMPANIES = [
    "Infosys", "TCS", "Wipro", "HCL Technologies", "Tech Mahindra",
    "Cognizant", "Accenture India", "IBM India", "Capgemini", "Mindtree",
    "Reliance Industries", "HDFC Bank", "ICICI Bank", "Flipkart", "Zomato",
    "Swiggy", "Ola", "Paytm", "MakeMyTrip", "Byju's",
]

DEPARTMENTS = [
    "Engineering", "Marketing", "Finance", "Human Resources", "Operations",
    "Sales", "Product Management", "Design", "Data Science", "Customer Support",
]

FEEDBACK_POSITIVE = [
    "Excellent experience overall. Highly recommended!",
    "Very satisfied with the service. Keep up the good work.",
    "Great initiative. Looking forward to more such events.",
    "Really helpful and well-organized. Thank you!",
    "Impressed with the quality and attention to detail.",
    "Everything was smooth and professional. Well done.",
    "Good experience. Would definitely participate again.",
    "The program was informative and engaging.",
]

FEEDBACK_NEUTRAL = [
    "The experience was decent. There is room for improvement.",
    "Overall okay. Some aspects could be better.",
    "Satisfactory. Would appreciate more clarity on certain points.",
    "Reasonable effort. A few minor issues noticed.",
    "Average experience. Improvements in communication would help.",
]

SUGGESTIONS = [
    "Please provide more detailed instructions beforehand.",
    "Would appreciate better scheduling and time management.",
    "Adding online resources would be helpful.",
    "More interactive sessions would improve engagement.",
    "Consider sending reminder emails before the event.",
    "Better coordination between teams would improve things.",
    "A feedback session at the end would be valuable.",
]

YES_NO_OPTIONS = {
    "yes": ["Yes", "Yes, definitely", "Agreed", "I agree", "True", "Correct"],
    "no": ["No", "Not really", "Disagree", "I disagree", "False", "Incorrect"],
}

GENDER_OPTIONS = ["Male", "Female", "Other", "Prefer not to say"]

AGE_GROUPS = ["18-24", "25-30", "31-40", "41-50", "51+", "Below 18"]

EDUCATION = [
    "High School", "Diploma", "Bachelor's Degree", "Master's Degree",
    "MBA", "PhD", "Other",
]


def generate_indian_name() -> dict:
    gender = random.choice(["male", "female"])
    first = random.choice(FIRST_NAMES_MALE if gender == "male" else FIRST_NAMES_FEMALE)
    last = random.choice(LAST_NAMES)
    full = f"{first} {last}"
    username_styles = [
        f"{first.lower()}.{last.lower()}",
        f"{first.lower()}{random.randint(10, 99)}",
        f"{first.lower()}_{last.lower()}",
        f"{last.lower()}.{first.lower()}",
        f"{first.lower()}{last.lower()}{random.randint(1, 9)}",
    ]
    email = f"{random.choice(username_styles)}@{random.choice(EMAIL_DOMAINS)}"
    mobile_prefix = random.choice(["6", "7", "8", "9"])
    mobile = f"{mobile_prefix}{''.join([str(random.randint(0,9)) for _ in range(9)])}"
    return {
        "first": first,
        "last": last,
        "full": full,
        "gender": gender,
        "email": email,
        "mobile": mobile,
        "mobile_formatted": f"+91 {mobile[:5]} {mobile[5:]}",
        "city": random.choice(CITIES),
        "state": random.choice(STATES),
        "age": random.randint(18, 45),
        "pincode": f"{random.randint(100, 999)}{random.randint(100, 999)}",
        "college": random.choice(COLLEGES),
        "company": random.choice(COMPANIES),
        "department": random.choice(DEPARTMENTS),
    }


def smart_answer(label: str, field_type: str, person: dict) -> str:
    """Generate a contextually appropriate answer based on question label."""
    label_lower = label.lower()

    # Name fields
    if any(k in label_lower for k in ["full name", "your name", "name"]):
        if "first" in label_lower:
            return person["first"]
        if "last" in label_lower or "surname" in label_lower:
            return person["last"]
        return person["full"]

    # Contact
    if any(k in label_lower for k in ["email", "e-mail", "mail id"]):
        return person["email"]
    if any(k in label_lower for k in ["phone", "mobile", "contact", "whatsapp", "number"]):
        return person["mobile"]

    # Location
    if "city" in label_lower or "location" in label_lower:
        return person["city"]
    if "state" in label_lower:
        return person["state"]
    if "pincode" in label_lower or "pin code" in label_lower or "zip" in label_lower:
        return person["pincode"]
    if "address" in label_lower:
        return f"{random.randint(1,99)}, {random.choice(['MG Road', 'Residency Road', 'Brigade Road', 'Park Street'])}, {person['city']}"

    # Demographics
    if "age" in label_lower:
        if field_type == "text":
            return str(person["age"])
        return random.choice(AGE_GROUPS)
    if "gender" in label_lower or "sex" in label_lower:
        return "Male" if person["gender"] == "male" else "Female"
    if "dob" in label_lower or "date of birth" in label_lower or "birth" in label_lower:
        year = datetime.now().year - person["age"]
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        return f"{day:02d}/{month:02d}/{year}"

    # Education
    if "college" in label_lower or "institution" in label_lower or "university" in label_lower:
        return person["college"]
    if "qualification" in label_lower or "education" in label_lower or "degree" in label_lower:
        return random.choice(EDUCATION)
    if "branch" in label_lower or "stream" in label_lower or "specialization" in label_lower:
        return random.choice(["Computer Science", "Electronics", "Mechanical", "Civil", "Information Technology", "MBA"])
    if "year" in label_lower and any(k in label_lower for k in ["study", "batch", "pass", "graduation"]):
        return str(random.randint(2018, 2026))
    if "cgpa" in label_lower or "gpa" in label_lower or "percentage" in label_lower or "marks" in label_lower:
        return f"{random.uniform(6.5, 9.5):.2f}"

    # Work
    if "company" in label_lower or "organization" in label_lower or "employer" in label_lower:
        return person["company"]
    if "department" in label_lower or "team" in label_lower:
        return person["department"]
    if "designation" in label_lower or "role" in label_lower or "position" in label_lower:
        return random.choice(["Software Engineer", "Manager", "Analyst", "Consultant", "Developer", "Designer"])
    if "experience" in label_lower:
        return f"{random.randint(1, 10)} years"
    if "salary" in label_lower or "ctc" in label_lower:
        return f"{random.randint(4, 25)} LPA"

    # Feedback / ratings
    if "rating" in label_lower or "rate" in label_lower or "score" in label_lower:
        return str(random.randint(7, 10))
    if "feedback" in label_lower or "review" in label_lower or "comment" in label_lower:
        return random.choice(FEEDBACK_POSITIVE + FEEDBACK_NEUTRAL)
    if "suggestion" in label_lower or "improve" in label_lower or "recommend" in label_lower:
        return random.choice(SUGGESTIONS)
    if "reason" in label_lower or "why" in label_lower:
        return random.choice(["Good quality", "Convenient", "Recommended by friend", "Affordable pricing", "Easy to use"])
    if "how did you hear" in label_lower or "source" in label_lower:
        return random.choice(["Social Media", "Friend Referral", "Google Search", "Email", "WhatsApp"])

    # Dates
    if "date" in label_lower:
        future_date = datetime.now() + timedelta(days=random.randint(1, 60))
        return future_date.strftime("%d/%m/%Y")

    # Rollno / ID
    if "roll" in label_lower or "student id" in label_lower or "reg" in label_lower:
        return f"{random.randint(10000, 99999)}"

    # Default fallback
    return random.choice([
        "Good", "Satisfactory", "Yes", "Applicable",
        f"{person['first']} from {person['city']}", "N/A",
    ])


# ─────────────────────────────────────────────
#  FORM FILLER ENGINE
# ─────────────────────────────────────────────

class GoogleFormFiller:
    def __init__(self, url: str, headless: bool = False, delay: float = 0.5):
        self.url = url
        self.headless = headless
        self.delay = delay

    async def _human_type(self, element, text: str):
        """Type text with slight random delays to mimic human typing."""
        await element.click()
        await element.fill("")
        for char in text:
            await element.type(char, delay=random.uniform(20, 80))
        await asyncio.sleep(self.delay * 0.3)

    async def _get_label(self, question_el) -> str:
        """Extract question label text."""
        try:
            label_el = await question_el.query_selector("[role='heading'], .freebirdFormviewerComponentsQuestionBaseTitle")
            if label_el:
                return (await label_el.inner_text()).strip()
        except Exception:
            pass
        try:
            return (await question_el.inner_text()).strip()[:100]
        except Exception:
            return ""

    async def fill_form(self, person: dict) -> bool:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=100 if not self.headless else 0,
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            )
            page = await context.new_page()

            try:
                print(f"\n  → Loading form for {person['full']} ({person['email']})")
                await page.goto(self.url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(1)

                filled_pages = 0
                while True:
                    await asyncio.sleep(0.8)
                    questions = await page.query_selector_all(
                        ".freebirdFormviewerComponentsQuestionBaseRoot, "
                        "[data-params*='required'], "
                        ".freebirdFormviewerViewItemsItemItem"
                    )

                    if not questions:
                        # Try alternate selectors
                        questions = await page.query_selector_all("div[jsmodel]")

                    print(f"     Found {len(questions)} question block(s) on page {filled_pages + 1}")

                    for q in questions:
                        label = await self._get_label(q)
                        if not label:
                            continue

                        # ── Short text / Long text ──────────────────────────
                        text_inputs = await q.query_selector_all("input[type='text'], input[type='email'], input[type='tel'], input[type='number']")
                        for inp in text_inputs:
                            if not await inp.is_visible():
                                continue
                            answer = smart_answer(label, "text", person)
                            await self._human_type(inp, answer)
                            print(f"     ✎  [{label[:40]}] → {answer}")

                        textareas = await q.query_selector_all("textarea")
                        for ta in textareas:
                            if not await ta.is_visible():
                                continue
                            answer = smart_answer(label, "textarea", person)
                            await self._human_type(ta, answer)
                            print(f"     ✎  [{label[:40]}] → {answer[:40]}...")

                        # ── Radio buttons ───────────────────────────────────
                        radios = await q.query_selector_all("[role='radio']")
                        if radios:
                            visible_radios = [r for r in radios if await r.is_visible()]
                            if visible_radios:
                                chosen = random.choice(visible_radios)
                                label_text = await chosen.inner_text()
                                await chosen.click()
                                await asyncio.sleep(self.delay * 0.5)
                                print(f"     ○  [{label[:40]}] → {label_text.strip()}")

                        # ── Checkboxes ──────────────────────────────────────
                        checkboxes = await q.query_selector_all("[role='checkbox']")
                        if checkboxes:
                            visible_cb = [c for c in checkboxes if await c.is_visible()]
                            if visible_cb:
                                num_to_check = random.randint(1, min(2, len(visible_cb)))
                                chosen = random.sample(visible_cb, num_to_check)
                                for cb in chosen:
                                    await cb.click()
                                    await asyncio.sleep(0.2)
                                    cb_text = await cb.inner_text()
                                    print(f"     ☑  [{label[:40]}] → {cb_text.strip()}")

                        # ── Dropdowns ───────────────────────────────────────
                        selects = await q.query_selector_all("select")
                        for sel in selects:
                            if not await sel.is_visible():
                                continue
                            options = await sel.query_selector_all("option")
                            valid_options = []
                            for opt in options:
                                val = await opt.get_attribute("value")
                                if val and val not in ["", "__other_option__"]:
                                    valid_options.append(val)
                            if valid_options:
                                chosen = random.choice(valid_options)
                                await sel.select_option(chosen)
                                print(f"     ▾  [{label[:40]}] → {chosen}")

                        # ── Google Forms custom dropdown ────────────────────
                        dropdowns = await q.query_selector_all("[role='listbox'], .quantumWizMenuPaperselectEl")
                        for dd in dropdowns:
                            if not await dd.is_visible():
                                continue
                            await dd.click()
                            await asyncio.sleep(0.5)
                            options = await page.query_selector_all("[role='option']")
                            visible_opts = [o for o in options if await o.is_visible()]
                            if visible_opts:
                                pick = random.choice(visible_opts)
                                opt_text = await pick.inner_text()
                                await pick.click()
                                await asyncio.sleep(0.3)
                                print(f"     ▾  [{label[:40]}] → {opt_text.strip()}")

                        # ── Date fields ─────────────────────────────────────
                        date_inputs = await q.query_selector_all("input[type='date']")
                        for di in date_inputs:
                            if not await di.is_visible():
                                continue
                            rand_date = datetime.now() - timedelta(days=random.randint(365, 365 * 25))
                            await di.fill(rand_date.strftime("%Y-%m-%d"))
                            print(f"     📅 [{label[:40]}] → {rand_date.strftime('%Y-%m-%d')}")

                        # ── Scale / Linear scale ────────────────────────────
                        scale_items = await q.query_selector_all("[role='radio'][data-value]")
                        if scale_items:
                            visible_scale = [s for s in scale_items if await s.is_visible()]
                            if visible_scale:
                                # Bias toward higher ratings
                                chosen = random.choices(
                                    visible_scale,
                                    weights=[1] * max(1, len(visible_scale) - 3) + [3, 4, 5],
                                    k=1
                                )[0]
                                val = await chosen.get_attribute("data-value")
                                await chosen.click()
                                await asyncio.sleep(0.3)
                                print(f"     ★  [{label[:40]}] → {val}")

                    filled_pages += 1
                    await asyncio.sleep(0.5)

                    # Check for Next / Submit button
                    next_btn = await page.query_selector("[jsname='OCpkoe'], [jsname='M2UYVd']")
                    submit_btn = await page.query_selector(
                        "[jsname='M2UYVd'][data-is-primary='true'], "
                        "div[role='button'][jsname='OCpkoe']"
                    )

                    # Generic approach: look for visible buttons containing Next/Submit text
                    all_btns = await page.query_selector_all("div[role='button'], button")
                    action_btn = None
                    for btn in all_btns:
                        if not await btn.is_visible():
                            continue
                        txt = (await btn.inner_text()).strip().lower()
                        if txt in ["next", "submit", "आगे बढ़ें", "जमा करें", "submit form"]:
                            action_btn = btn
                            break

                    if not action_btn:
                        # Fallback: any primary colored button
                        action_btn = await page.query_selector(".appsMaterialWizButtonPaperbuttonLabel")

                    if action_btn:
                        btn_text = (await action_btn.inner_text()).strip()
                        print(f"\n  → Clicking: '{btn_text}'")
                        await action_btn.click()
                        await asyncio.sleep(2)

                        # Check if form was submitted (confirmation message)
                        body_text = await page.inner_text("body")
                        if any(k in body_text.lower() for k in [
                            "your response has been recorded",
                            "response recorded",
                            "thank you",
                            "submitted",
                            "धन्यवाद",
                            "सफलतापूर्वक",
                        ]):
                            print(f"  ✅ Form submitted successfully for {person['full']}!")
                            await browser.close()
                            return True

                        if "next" in btn_text.lower():
                            continue  # Multi-page form, go to next page
                    else:
                        print("  ⚠  No action button found. Form may be already submitted or requires manual check.")
                        break

                    if filled_pages > 10:
                        print("  ⚠  Too many pages. Stopping.")
                        break

            except PlaywrightTimeout:
                print(f"  ✗  Timeout loading the form.")
            except Exception as e:
                print(f"  ✗  Error: {e}")
            finally:
                await browser.close()

        return False


# ─────────────────────────────────────────────
#  CLI ENTRY POINT
# ─────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="🤖 Google Form Auto-Filler with Indian personas",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python form_filler.py --url "https://forms.gle/abc123" --count 3
  python form_filler.py --url "https://forms.gle/abc123" --count 10 --headless
  python form_filler.py --url "https://forms.gle/abc123" --count 5 --delay 1.5
        """
    )
    parser.add_argument("--url", required=True, help="Google Form URL")
    parser.add_argument("--count", type=int, default=1, help="Number of submissions (default: 1)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (no browser window)")
    parser.add_argument("--delay", type=float, default=0.5, help="Typing delay multiplier (default: 0.5)")
    parser.add_argument("--gap", type=float, default=3.0, help="Gap between submissions in seconds (default: 3)")

    args = parser.parse_args()

    print("\n" + "═" * 55)
    print("  🤖  Google Form Auto-Filler  |  Indian Persona Mode")
    print("═" * 55)
    print(f"  Form URL : {args.url}")
    print(f"  Count    : {args.count} submission(s)")
    print(f"  Mode     : {'Headless' if args.headless else 'Visual (browser visible)'}")
    print(f"  Gap      : {args.gap}s between submissions")
    print("═" * 55)

    filler = GoogleFormFiller(args.url, headless=args.headless, delay=args.delay)
    success, failed = 0, 0

    for i in range(args.count):
        person = generate_indian_name()
        print(f"\n[{i+1}/{args.count}] Persona: {person['full']} | {person['mobile']} | {person['email']}")

        result = await filler.fill_form(person)
        if result:
            success += 1
        else:
            failed += 1

        if i < args.count - 1:
            wait = args.gap + random.uniform(0, 2)
            print(f"\n  ⏳ Waiting {wait:.1f}s before next submission...")
            await asyncio.sleep(wait)

    print("\n" + "═" * 55)
    print(f"  📊 Summary: {success} success, {failed} failed out of {args.count}")
    print("═" * 55 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
