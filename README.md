# Resume.io to PDF

**Author:** Shakkar Daddy

Download your resume from [resume.io](https://resume.io) as a PDF file.

Open the application, enter your resume `renderingToken`, and click the download button.
It will automatically download the first page of your resume as an image, convert it to a PDF file, and run OCR to extract the text.

> **Note:** Due to recent changes in resume.io's rendering service, only the first page of the resume can be downloaded and the maximum image resolution is capped at 2000px.

### How to find your renderingToken

Resumes: https://resume.io/api/app/resumes

Cover Letters: https://resume.io/api/app/cover-letters/

You will see a list of your resumes. Find the one you want to download and get the `renderingToken` from the payload.

### How to run the application

Go to the project's root folder:

```bash
cd shakkar-resumeio-pdf
```

Build the image:

```bash
docker build -t shakkar-resumeio-pdf .
```

Run the container:

```bash
docker run -p 8000:8000 shakkar-resumeio-pdf
```

Open your browser and access http://localhost:8000

### Disclaimer

Please be advised that this application is designed for preview purposes only.

By utilizing this tool, you explicitly agree to adhere to all applicable laws and regulations governing the use of such services.
Shakkar Daddy absolves themselves of any responsibility for potential damages or harm resulting from its utilization.

It is essential to visit the pricing page on Resume.io to explore fair and affordable options for accessing the resume downloading service directly through the official channels provided by Resume.io.
Shakkar Daddy emphasizes the importance of supporting the platform by subscribing to their services and discourages the use of this application as a substitute for legitimate and paid access.
