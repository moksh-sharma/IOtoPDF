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

### Deploy on Oracle Cloud (free forever)

**1. Create a free VM**

- Sign up at [cloud.oracle.com](https://cloud.oracle.com)
- **Compute → Instances → Create instance**
- Image: **Ubuntu 22.04** (or 24.04)
- Shape: **Ampere A1 Flex** (Always Free) - 1 OCPU, 6 GB RAM is enough
- Add your **SSH public key**
- Create

**2. Open firewall ports (Oracle Console)**

- **Networking → Virtual Cloud Networks** → your VCN → **Security List**
- Add **Ingress** rules:
  - TCP port **22** (SSH)
  - TCP port **80** (HTTP)
  - TCP port **443** (HTTPS, optional for later)

**3. SSH into the VM and deploy**

```bash
ssh ubuntu@YOUR_PUBLIC_IP

git clone https://github.com/moksh-sharma/IOtoPDF.git
cd IOtoPDF
bash scripts/oracle-vm-setup.sh
```

If you were added to the `docker` group, log out and back in first, or use `sudo docker compose` commands.

**4. Visit your site**

Open `http://YOUR_PUBLIC_IP` in a browser - it is public for anyone to use.

**Update later:**

```bash
cd ~/IOtoPDF && git pull && sudo docker compose up -d --build
```

### Disclaimer

Please be advised that this application is designed for preview purposes only.

By utilizing this tool, you explicitly agree to adhere to all applicable laws and regulations governing the use of such services.
Shakkar Daddy absolves themselves of any responsibility for potential damages or harm resulting from its utilization.

It is essential to visit the pricing page on Resume.io to explore fair and affordable options for accessing the resume downloading service directly through the official channels provided by Resume.io.
Shakkar Daddy emphasizes the importance of supporting the platform by subscribing to their services and discourages the use of this application as a substitute for legitimate and paid access.
