import requests
import time

with open("test_res.txt", "w") as f:
    f.write("""Alice Johnson
Email: alice@example.com | Phone: 9876543210
Summary: Experienced Python Developer with 2 years of experience building web applications using Django and REST APIs.
Skills: Python, Django, Flask, REST API, SQL, PostgreSQL, Git, Docker
Experience:
Junior Developer at TechCorp - Built REST API services
Projects:
E-commerce App - Django, PostgreSQL, Redis
Education: B.Tech in Computer Science, 2022
Certifications: AWS Cloud Practitioner
""")

start = time.time()
with open("test_res.txt", "rb") as f:
    r = requests.post("http://127.0.0.1:5000/", files={"resume": f}, data={
        "target_role": "Python Developer",
        "job_description": "We need a Python Developer with experience in Django, REST APIs, SQL, Git, Docker and CI/CD."
    })
print(f"Status: {r.status_code}, Time: {time.time() - start:.2f}s")
if r.status_code == 200:
    import re
    ats = re.search(r"ATS Score.*?(\d+)", r.text)
    jd = re.search(r"JD Match.*?(\d+\.?\d*)", r.text)
    if ats: print(f"ATS found in response: {ats.group(1)}")
    if jd: print(f"JD match found in response: {jd.group(1)}")
