# Making the Switch to Docker Hardened Images

Switching to a Docker Hardened Image is straightforward. All we need to do is replace the base image `python:3.11` with a DHI equivalent.

Docker Hardened Images come in two variants:

* Dev variant (`demonstrationorg/dhi-python:3.11-debian13-dev`) – includes a shell and package managers, making it suitable for building and testing.
* Runtime variant (`demonstrationorg/dhi-python:3.11-debian13`) – stripped down to only the essentials, providing a minimal and secure footprint for production.

This makes them perfect for use in multi-stage Dockerfiles. We can build the app in the dev image, then copy the built application into the runtime image, which will serve as the base for production.

1. Update the `Dockerfile` to use the `demonstrationorg/dhi-python:3.11-debian13-dev` as a `dev` stage image and `demonstrationorg/dhi-python:3.11-debian13` as a `runtime` image

For a multi-stage build approach:
```dockerfile
# Stage 1: Build stage
FROM demonstrationorg/dhi-python:3.11-debian13-dev AS dev

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Stage 2: Runtime stage
FROM demonstrationorg/dhi-python:3.11-debian13 AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

# Copy virtual environment from dev stage
COPY --from=dev /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --from=dev /app/app.py .

# Expose port
EXPOSE 8888

# Run the application
CMD ["python", "app.py"]
```

2. Looking back at the output for the `scout quickview` the `No default non-root user found` policy was not met. To resolve this we tipically need to add a non-root user to the Dockerfile description. The good news is that the DHI comes with nonroot user built-in so no changes should be made.

3. Now Let's rebuild and scan the new image:
```bash
docker buildx build --provenance=true --sbom=true -t $$orgname$$/demo-python-dhi:v1 .
```
```bash
docker scout policy $$orgname$$/demo-python-dhi:v1 --org $$orgname$$
```
You would see the similar output:
```plaintext no-copy-button
 Policy status  SUCCESS  (10/10 policies met)

  Status │                       Policy                        │           Results            
─────────┼─────────────────────────────────────────────────────┼──────────────────────────────
  ✓      │ AGPL v3 licenses found                              │    0 packages                
  ✓      │ Default non-root user                               │                              
  ✓      │ No AGPL v3 licenses                                 │    0 packages                
  ✓      │ No embedded secrets                                 │    0 deviations              
  ✓      │ No embedded secrets (Rego)                          │    0 deviations              
  ✓      │ No fixable critical or high vulnerabilities         │    0C     0H     0M     0L   
  ✓      │ No high-profile vulnerabilities                     │    0C     0H     0M     0L   
  ✓      │ No unapproved base images                           │    0 deviations              
  ✓      │ Supply chain attestations                           │    0 deviations              
  ✓      │ Valid Docker Hardened Image (DHI) or DHI base image │    0 deviations              
```
Hooray! There are zero CVEs and Policy violations now!

**Validate that the app works as expected**

Last but not least, after migrating to a DHI base image, we should verify that the application still functions as expected.

1. To do so, we can either start the app locally with:
```bash
docker run --rm -d --name demo-python -p 8888:8888 demonstrationorg/demo-python-dhi:v1
```
and navigate to :tabLink[This link]{href="http://localhost:8888" title="Web app"} to validate that the app is up and running.

Then stop the container:
```bash
docker stop demo-python
```