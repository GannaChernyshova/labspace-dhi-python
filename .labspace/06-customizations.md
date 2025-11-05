# Customizations

Customize a Docker Hardened Image (DHI) base image with Chromium by adding it as an OCI artifact via Docker Hub. This eliminates the need to install Chromium during Docker builds, reducing build time.

Reference: [Docker Hub DHI Customization Workflow](https://docs.docker.com/dhi/how-to/customize/)

## Prerequisites

- Docker Hub organization with mirrored DHI repository
- Organization owner permissions (for mirroring)
- Access to mirrored DHI repository (for customizing)

## Step 1: Create Chromium OCI Artifact Image

Build a custom OCI artifact image based on DHI Debian base that installs Chromium and Chromedriver via apt-get.

**File: `Dockerfile.chromium-oci`**

```dockerfile
# Base Hardened Debian image
FROM demonstrationorg/dhi-debian-base:trixie-debian13

RUN apt-get update && \
    apt-get install -y \
        chromium \
        chromium-driver \
        fonts-liberation \
        libu2f-udev \
        xdg-utils \
        libglib2.0-0 \
        libnss3 \
        libnspr4 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libgbm1 \
        libxkbcommon0 \
        libxcomposite1 \
        libxdamage1 \
        libxfixes3 \
        libxrandr2 \
        libasound2 \
        libpango-1.0-0 \
        libcairo2 \
        libatspi2.0-0 \
        libxshmfence1 \
        --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Optional: verify installation
RUN chromium --version
```

**Build and push:**

For a single platform (e.g., amd64):
```bash
docker buildx build -f Dockerfile.chromium-oci -t demonstrationorg/chromium-oci:latest --platform linux/amd64 --push .
```
> **Note**: Ensure the chromium-oci image is built for the same platform(s) as your target DHI customization.

**Verified paths in the custom chromium-oci image:**
- Chromium binary: `/usr/bin/chromium` or `/usr/bin/chromium-browser`
- Chromedriver: `/usr/bin/chromedriver`
- Chromium libraries: `/usr/lib/chromium`
- Shared libraries: `/lib/x86_64-linux-gnu` and `/usr/lib/x86_64-linux-gnu`
- Fonts: `/usr/share/fonts/truetype/liberation`

## Step 2: Customize DHI Base Image via Docker Hub

1. Sign in to Docker Hub
2. Navigate to your organization
3. Select **Hardened Images** > **Management**
4. Find the mirrored `dhi-python` repository
5. Select **Customize** from the menu
6. Select image version: `3.11-debian13-dev`
7. In the **OCI artifacts** section:
   - **Repository**: Select `chromium-oci`
   - **Tag**: Select `latest`
   - **Include paths** (critical - include all of these):
     - `/usr/bin` (includes chromium, chromium-browser, chromedriver, and xdg-utils)
     - `/usr/lib/chromium`
     - `/usr/share/chromium`
     - `/usr/share/fonts`
     - **Architecture-specific library paths** (use the one matching your target platform):
       - For **linux/amd64** (x86_64): `/lib/x86_64-linux-gnu` and `/usr/lib/x86_64-linux-gnu`
       - For **linux/arm64** (aarch64): `/lib/aarch64-linux-gnu` and `/usr/lib/aarch64-linux-gnu`
     - `/lib/udev` and `/usr/lib/udev` (UDEV rules)
     - `/etc/alternatives` and `/etc/chromium.d` (configuration)
     
   > **Important**: 
   > - You must include the architecture-specific library paths to ensure shared libraries like `libglib-2.0.so.0` are available. Without these, chromedriver will fail with "cannot open shared object file" errors.
   > - The chromium-oci OCI artifact must be built for the same platform(s) as your target DHI customization. Use `--platform linux/amd64,linux/arm64` when building to support multiple platforms.
8. Select **Next: Configure**
9. Configure:
   - **Tag suffix**: `chromium` (creates tag `3.11-debian13-dev_chromium`)
   - **Platforms**: Select target platforms
10. Select **Create Customization**

**Result:** Customized image available as `$$orgname$$/dhi-python:3.11-debian13-dev_chromium`

## Step 3: Update Dockerfile

### Example: Build Failure Without Chromium

Using the base DHI image without Chromium causes e2e tests to fail:

```dockerfile
# Stage 1: Build stage
FROM demonstrationorg/dhi-python:3.11-debian13-dev AS dev

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 
ENV PORT=8888

WORKDIR /app

# Add chromedriver to PATH if it exists from browserless/chrome OCI artifact
ENV PATH="/usr/src/app/node_modules/chromedriver/bin:$PATH"

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install pytest for running tests
RUN pip install --no-cache-dir pytest

# Copy application code and test files
COPY app.py .
COPY test_e2e.py .
COPY run_tests.sh .

# Make test script executable and run e2e tests
RUN chmod +x run_tests.sh && ./run_tests.sh
```

**Build command:**

```bash
docker buildx build -t demo-python-test:without-chromium .
```

**Expected error:**

```
test_e2e.py::test_app_displays_hello_world FAILED
...
Error initializing Chrome driver: Message: 'chromedriver' executable needs to be in PATH
```

### Solution: Use Customized DHI Image

**File: `Dockerfile`**

```dockerfile
# Stage 1: Build stage
FROM demonstrationorg/dhi-python-anna:3.11-debian13-dev_chromium AS dev
```

**Build command:**

```bash
docker buildx build -t demo-python-test:with-chromium .
```

**Build benefits:**
- Chromium pre-installed: eliminates `apt-get install` step
- Better caching: customized base image is cached
- Security attestations: built through Docker Hub with attestations
- E2E tests: run automatically during build via `run_tests.sh`
- Minimal runtime: test dependencies only in dev stage
