import os
import requests
import boto3

page = 1
data = requests.get(f"https://www.themuse.com/api/public/jobs?page={page}").json()
headers = "publication_date, job_name, job_type, job_location, company_name\n"


def has_header():
    with open(f"data-{page}.csv", "r") as a:
        if not a.readline():
            return False


def create_csv_string(line: dict) -> str:
    publication_date = line.get("publication_date", "").split("T")[0]
    job_type = line.get("type", "")
    job_name = line.get("name", "")
    company_name = line.get("company", {}).get("name", "")
    job_city, job_country = line.get("locations", [{}])[0].get("name", "").split(",")
    return f"{publication_date}, {job_name}, {job_type}, {company_name}, {job_city}, {job_country}\n"


with open(f"data-{page}.csv", "w") as f:
    if not has_header():
        f.write(headers)

    for line in data.get("results") or []:
        try:
            f.write(create_csv_string(line))
        except Exception as err:
            print(err)

s3 = boto3.resource("s3")
s3.meta.client.upload_file(
    f"data-{page}.csv", os.environ["S3BUCKET"], f"data-{page}.csv"
)
