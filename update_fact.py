import random
import re

# Comprehensive list of Computer Science facts
CS_FACTS = [
    "The first computer bug was an actual moth found in Harvard's Mark II computer in 1947.",
    "The first domain name ever registered was symbolics.com on March 15, 1985.",
    "Python was named after Monty Python, not the snake.",
    "The first 1GB hard drive, released in 1980, weighed over 500 pounds and cost $40,000.",
    "The first computer mouse was made of wood and invented by Doug Engelbart in 1964.",
    "CAPTCHA stands for 'Completely Automated Public Turing test to tell Computers and Humans Apart'.",
    "The first programming language was Fortran, developed in 1957 by IBM.",
    "The term 'debugging' was popularized by Grace Hopper after finding the moth.",
    "The first computer virus was created in 1983 and was called 'Elk Cloner'.",
    "Google's original name was 'Backrub'.",
    "The first webcam was created at Cambridge University to monitor a coffee pot.",
    "The average person blinks 20 times per minute, but only 7 times per minute when using a computer.",
    "The first electronic computer, ENIAC, weighed 30 tons and took up 1800 square feet.",
    "90% of the world's currency only exists on computers.",
    "The first computer game, 'Spacewar!', was created in 1962 at MIT.",
    "Email existed before the World Wide Web.",
    "The QWERTY keyboard layout was designed to slow down typing to prevent typewriter jams.",
    "The first computer programmer was Ada Lovelace in the 1840s.",
    "Facebook's blue color scheme is because Mark Zuckerberg is red-green colorblind.",
    "The 'Save' icon is a floppy disk, which many young people have never seen.",
    "YouTube was originally designed as a video dating site.",
    "The first Apple logo featured Sir Isaac Newton sitting under an apple tree.",
    "C programming language was created in just one year.",
    "The term 'cyberspace' was coined by sci-fi author William Gibson in 1982.",
    "Linux is named after its creator Linus Torvalds.",
    "The first banner ad on the web had a 44% click-through rate.",
    "HP, Microsoft, and Apple all started in garages.",
    "The first alarm clock could only ring at 4 AM.",
    "NASA's Apollo 11 guidance computer had less processing power than a modern smartphone.",
    "The first known computer password was used in the early 1960s at MIT."
]

def update_readme():
    # Read the current README
    with open('README.md', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Select a random fact
    new_fact = random.choice(CS_FACTS)
    
    # Define the pattern to find the fact section
    pattern = r'(- ⚡ Fun fact \*\*).*?(\*\*)'
    replacement = f'\\1{new_fact}\\2'
    
    # Replace the fact
    updated_content = re.sub(pattern, replacement, content)
    
    # If the pattern wasn't found, add it after the email line
    if updated_content == content:
        email_pattern = r'(- 📫 How to reach me \*\*surajyadav200701@gmail\.com\*\*)'
        updated_content = re.sub(
            email_pattern, 
            f'\\1\n- ⚡ Fun fact **{new_fact}**',
            content
        )
    
    # Write the updated content back
    with open('README.md', 'w', encoding='utf-8') as file:
        file.write(updated_content)
    
    print(f"✅ README updated with fact: {new_fact}")

if __name__ == "__main__":
    update_readme()
