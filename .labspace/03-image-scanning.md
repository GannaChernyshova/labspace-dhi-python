# Image scanning

## Exploring the app

This demo repository contains a Hello World Python application consisting of a basic Flask server and Dockerfile pointing to a Python 3.11 base image.
The app logic is implemented in the :fileLink[app.py]{path="app.py"} file. 


## Dockerfile

To follow modern best practices, we want to containerize the app and eventually deploy it to production. Before doing so, we must ensure the image is secure by using [Docker Scout](https://www.docker.com/products/docker-scout/)

Our Dockerfile uses a single-stage build approach and is based on the `python:3.11` image.

**Let’s build our image with SBOM and provenance metadata**
This lab already has a :fileLink[Dockerfile]{path="Dockerfile"}, so you can easily build the image.

1. Use the `docker build` command to build the image:
We'll use the buildx command (a Docker CLI plugin that extends the docker build) with the –provenance=true  and –sbom=true flags. These options attach [build attestations](https://docs.docker.com/build/metadata/attestations/) to the image, which Docker Scout uses to provide more detailed and accurate security analysis.

```bash
docker buildx build --provenance=true --sbom=true -t $$orgname$$/demo-python-doi:v1 .
```

2. Now that you have an image let's analyze it.
Use the `docker scout cves` command to list all discovered vulnerabilities:

```bash
docker scout cves $$orgname$$/demo-python-doi:v1
```

If your account is part of an paid organization you can analyze the image with the `docker scout quickview` command to see the policy complince:

```bash
docker scout quickview $$orgname$$/demo-python-doi:v1
```
You would see the similar output:
```plaintext no-copy-button
Target               │  demonstrationorg/demo-python-dhi:v1  │    0C     1H     5M   142L     2?   
    digest           │  a7cc248d657a                         │                                     
  Base image         │  python:3.11                          │    0C     1H     5M   142L     2?   
  Updated base image │  python:3.11-slim                     │    0C     0H     2M    20L          
                     │                                       │           -1     -3   -122     -2   

Policy status  FAILED  (5/10 policies met)

  Status │                              Policy                              │           Results            
─────────┼──────────────────────────────────────────────────────────────────┼──────────────────────────────
  !      │ AGPL v3 licenses found                                           │    3 packages                
  !      │ No default non-root user found                                   │                              
  !      │ AGPL v3 licenses found                                           │    3 packages                
  ✓      │ No embedded secrets                                              │    0 deviations              
  ✓      │ No embedded secrets (Rego)                                       │    0 deviations              
  ✓      │ No fixable critical or high vulnerabilities                      │    0C     0H     0M     0L   
  ✓      │ No high-profile vulnerabilities                                  │    0C     0H     0M     0L   
  !      │ Unapproved base images found                                     │    1 deviation               
  ✓      │ Supply chain attestations                                        │    0 deviations              
  !      │ Invalid or Missing Docker Hardened Image (DHI) or DHI base image │    1 deviation        
```

There are still few on the base image level. And the critical policies have failed:

    1. AGPL v3 licenses found
    2. No default non-root user found
    3. AGPL v3 licenses found
    4. Fixable critical or high vulnerabilities found
    5. Unapproved base images found
    6. Invalid or Missing Docker Hardened Image (DHI) or DHI base image
 This is where DHI comes into play.

