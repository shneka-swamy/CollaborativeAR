# CollaborativeAR

This repository contains the required documents for running the simulation of **SPARC**.

---

## Dataset

Download the dataset.

In the paper we predominantly use the **EuRoC dataset**:

https://www.research-collection.ethz.ch/entities/researchdata/bcaf173e-5dac-484b-bc37-faf97a594f1f

---

## Image Processing Pipeline

After downloading the images:

### 1. Downscale Images

Decrease the resolution of the image by `/4` using:

```
modify_image.py
```

### 2. Super-Resolution Processing

All the images that are **not blurred** (blur detection can be done using the `laplacian_blur.py` snippet) in each folder of the low-resolution dataset are converted into super-resolution images using the **AdC model**.

Follow instructions from:

https://github.com/Guaishou74851/AdcSR

No changes are made to images that are blurred.

To run the previous two steps together, follow the format provided in:

```
scripts/generate_dataset.sh
```

### 3. Combine Images

The resized images and the original blurred images are combined together using:

```
./utils/add_images.py
```

---

## SLAM Algorithm

### 1. Run SLAM

Once the images are received, run the SLAM algorithm.

For the experiments in the paper we use a **state-of-the-art Monocular-Inertial SLAM method**.

> **Note:** EuRoC comes with its own inertial file — copy it to the combined images folder before running the SLAM algorithm.

---

### 2. Enable Timing Logs

We use this pipeline to measure runtime and trajectory error while using super-resolution.

Apart from the general run, enable storing:

- LocalMapping time
- Tracking time

Instructions are available at:

https://github.com/UZ-SLAMLab/ORB_SLAM3

---

### 3. Run Simulation

After SLAM execution, the generated time files are used to run the simulation and determine results.

Run:

```
Simulation/main.py
```

Follow the running format provided in:

```
runSimulation.py
```

---

## Real World Implementation Notes

> Only the conversion of the original image to the low-resolution image is done on the **device**.

All other implementations must run on the **server**:

- Super-resolution
- ORB-SLAM3

A starting implementation exists in:

```
RealDevelopment/
```

---

### Scheduling Changes Required

For real-world deployment, the ORB-SLAM3 implementation must be modified.

Major components to implement:

- Resolution change
- Network communication
- AdCSR integration

---

## Simulation Folder

The `Simulation/` folder is **not required** for real-world implementation.
